"""Live GeM advance-search automation and bid-fit review panel.

Searches the official portal through the user's embedded browser session. It does not
bypass login/CAPTCHA or submit bids.
"""
import json
import re
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QPushButton, QListWidget, QListWidgetItem, QTextEdit, QMessageBox
)

ADVANCE_URL = "https://bidplus.gem.gov.in/all-bids"


class BidSearchPanel(QWidget):
    def __init__(self, browser, status_label, parent=None):
        super().__init__(parent)
        self.browser = browser
        self.status = status_label
        self.results = []
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(6)

        root.addWidget(QLabel("Search method"))
        self.mode = QComboBox()
        self.mode.addItems(["Bid number", "Ministry / organisation", "Location", "BOQ"])
        root.addWidget(self.mode)

        root.addWidget(QLabel("Bid number (Bid number search)"))
        self.bid_number = QLineEdit()
        self.bid_number.setPlaceholderText("e.g. GEM/2026/B/12345")
        root.addWidget(self.bid_number)

        root.addWidget(QLabel("Category (optional)"))
        self.category = QComboBox()
        self.category.setEditable(True)
        self.category.addItems([
            "Any category", "Goods", "Services", "Works", "Custom Bid",
            "Product", "Service"
        ])
        root.addWidget(self.category)

        root.addWidget(QLabel("Ministry / buyer (Ministry search)"))
        self.ministry = QLineEdit()
        self.ministry.setPlaceholderText("Choose a ministry / buyer")
        root.addWidget(self.ministry)

        root.addWidget(QLabel("State (Ministry or Location search)"))
        self.state = QLineEdit()
        self.state.setPlaceholderText("e.g. Maharashtra")
        root.addWidget(self.state)

        root.addWidget(QLabel("Organisation (optional)"))
        self.organisation = QLineEdit()
        self.organisation.setPlaceholderText("Organisation name")
        root.addWidget(self.organisation)

        root.addWidget(QLabel("City / location"))
        self.city = QLineEdit()
        self.city.setPlaceholderText("City or delivery area")
        root.addWidget(self.city)

        root.addWidget(QLabel("BOQ title / bid value"))
        self.boq = QLineEdit()
        self.boq.setPlaceholderText("BOQ title or value range")
        root.addWidget(self.boq)

        root.addWidget(QLabel("Business keywords (used to rank results)"))
        self.keywords = QLineEdit()
        self.keywords.setPlaceholderText("e.g. stationery, paper, toner, cleaning")
        root.addWidget(self.keywords)

        buttons = QHBoxLayout()
        self.search_btn = QPushButton("Search GeM bids")
        self.search_btn.clicked.connect(self.search)
        buttons.addWidget(self.search_btn)
        self.review_btn = QPushButton("AI review selected")
        self.review_btn.setObjectName("secondary")
        self.review_btn.clicked.connect(self.review_selected)
        buttons.addWidget(self.review_btn)
        root.addLayout(buttons)

        root.addWidget(QLabel("Matching bids · select one to review"))
        self.list = QListWidget()
        self.list.setMinimumHeight(150)
        self.list.currentRowChanged.connect(self.show_details)
        root.addWidget(self.list)

        self.details = QTextEdit()
        self.details.setReadOnly(True)
        self.details.setPlaceholderText("Bid details and fit assessment will appear here.")
        self.details.setMinimumHeight(110)
        root.addWidget(self.details)

        open_btn = QPushButton("Open selected bid in GeM")
        open_btn.setObjectName("secondary")
        open_btn.clicked.connect(self.open_selected)
        root.addWidget(open_btn)

        note = QLabel(
            "Uses the live GeM page and its current login session. Search results and "
            "recommendations must be verified against the official bid document. "
            "Applying/submitting remains a manual decision."
        )
        note.setWordWrap(True)
        note.setObjectName("muted")
        root.addWidget(note)

    def search(self):
        mode = self.mode.currentText()
        self.list.clear()
        self.details.clear()
        self.results = []
        self.search_btn.setEnabled(False)
        self.status.setText("Opening GeM advance search and applying filters…")
        if "all-bids" not in self.browser.url().toString():
            self.browser.setUrl(__import__("PySide6").QtCore.QUrl(ADVANCE_URL))
            QTimer.singleShot(1800, lambda: self._run_search(mode))
        else:
            self._run_search(mode)

    def _run_search(self, mode):
        values = {
            "mode": mode,
            "bid": self.bid_number.text().strip(),
            "category": self.category.currentText().strip(),
            "ministry": self.ministry.text().strip(),
            "state": self.state.text().strip(),
            "organisation": self.organisation.text().strip(),
            "city": self.city.text().strip(),
            "boq": self.boq.text().strip(),
        }
        script = r"""
        (async () => {
          const v = __VALUES__;
          const wait = ms => new Promise(r => setTimeout(r, ms));
          const visible = e => !!e && !!(e.offsetWidth || e.offsetHeight || e.getClientRects().length);
          const click = e => { if(e) e.click(); };
          const setInput = (sel, value) => {
            const e = document.querySelector(sel);
            if (!e || !value) return !!e;
            const proto = e.tagName === 'TEXTAREA' ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
            const d = Object.getOwnPropertyDescriptor(proto, 'value');
            if (d && d.set) d.set.call(e, value); else e.value = value;
            e.dispatchEvent(new Event('input', {bubbles:true}));
            e.dispatchEvent(new Event('change', {bubbles:true}));
            return true;
          };
          const selectText = (sel, text) => {
            const e = document.querySelector(sel);
            if (!e || !text) return !!e;
            const opt = [...e.options].find(o => o.text.trim().toLowerCase().includes(text.toLowerCase()));
            if (!opt) return false;
            e.value = opt.value;
            e.dispatchEvent(new Event('change', {bubbles:true}));
            if (window.jQuery) window.jQuery(e).trigger('change');
            return true;
          };
          const select2Text = async (containerSel, text) => {
            if (!text || /any category/i.test(text)) return true;
            const c = document.querySelector(containerSel);
            if (!c) return false;
            click(c); await wait(250);
            const options = [...document.querySelectorAll('.select2-results__option, [role="option"]')].filter(visible);
            const match = options.find(o => o.textContent.trim().toLowerCase().includes(text.toLowerCase()));
            if (match) { click(match); await wait(250); return true; }
            const search = document.querySelector('.select2-container--open .select2-search__field');
            if (search) {
              search.value = text; search.dispatchEvent(new Event('input',{bubbles:true})); await wait(500);
              const opts = [...document.querySelectorAll('.select2-results__option, [role="option"]')].filter(visible);
              const m = opts.find(o => o.textContent.trim().toLowerCase().includes(text.toLowerCase()));
              if (m) { click(m); await wait(250); return true; }
            }
            document.body.click(); return false;
          };
          const tabs = {
            "Bid number": "#bid-tab", "Ministry / organisation": "#ministry-tab",
            "Location": "#location-tab", "BOQ": "#boq-tab"
          };
          click(document.querySelector(tabs[v.mode]));
          await wait(500);
          let filled = [], missing = [];
          const trySet = (sel,val,label) => { if(!val) return; (setInput(sel,val)?filled:missing).push(label); };
          const trySelect = (sel,val,label) => { if(!val || /any category/i.test(val)) return; (selectText(sel,val)?filled:missing).push(label); };
          if (v.mode === "Bid number") {
            if (!v.bid) missing.push("Bid number is required");
            else { trySet('#bno',v.bid,'bid number'); }
            if (v.category) await select2Text('#select2-categorybid-container',v.category);
            click(document.querySelector('#searchByBid'));
          } else if (v.mode === "Ministry / organisation") {
            if (v.ministry) {
              let ok = await select2Text('#select2-ministry-container, #select2-ministry-container span',v.ministry);
              if (!ok) ok = selectText('#ministry',v.ministry);
              (ok?filled:missing).push('ministry');
            } else missing.push('ministry is required');
            await wait(350);
            if (v.state) {
              let ok = await select2Text('#select2-buyer_state-container',v.state);
              if (!ok) ok = selectText('#buyer_state',v.state);
              (ok?filled:missing).push('state');
            } else missing.push('state is required');
            if (v.organisation) {
              let ok = await select2Text('#select2-organization-container',v.organisation);
              if (!ok) ok = selectText('#organization',v.organisation);
              (ok?filled:missing).push('organisation');
            }
            const btn = document.querySelector('#ministry-search button[type="submit"], #ministry-search input[type="submit"], #ministry-search .btn-primary, #ministry-search button');
            click(btn);
          } else if (v.mode === "Location") {
            if (v.state) {
              let ok = await select2Text('#select2-state_name_con-container',v.state);
              if (!ok) ok = selectText('#state_name_con',v.state);
              (ok?filled:missing).push('state');
            }
            if (v.city) {
              let ok = await select2Text('#select2-city_name_con-container',v.city);
              if (!ok) ok = selectText('#city_name_con',v.city);
              (ok?filled:missing).push('city');
            }
            const form = document.querySelector('#location-search');
            click(form && form.querySelector('button[type="submit"], input[type="submit"], .btn-primary, button'));
          } else if (v.mode === "BOQ") {
            if (v.boq) {
              let ok = await select2Text('#select2-boqtitle_con-container',v.boq);
              if (!ok) ok = selectText('#boqtitle_con',v.boq);
              (ok?filled:missing).push('BOQ title');
            }
            const form = document.querySelector('#boq-search');
            click(form && form.querySelector('button[type="submit"], input[type="submit"], .btn-primary, button'));
          }
          await wait(1800);
          const resultRoot = document.querySelector('#result, section#result, .search-result, #bid-list') || document.body;
          const anchors = [...resultRoot.querySelectorAll('a[href]')];
          const candidates = [];
          const seen = new Set();
          for (const a of anchors) {
            const tr = a.closest('tr');
            const card = a.closest('.card, .panel, .row, li, article') || tr || a.parentElement;
            const text = (card?.innerText || a.innerText || '').replace(/\s+/g,' ').trim();
            const href = a.href || '';
            if (!text || text.length < 12 || seen.has(href + text.slice(0,50))) continue;
            if (!/bid|tender|gem\/\d{4}|view|details|boq/i.test(text + ' ' + href)) continue;
            seen.add(href + text.slice(0,50));
            candidates.push({title:(a.innerText||'').trim().slice(0,180), text:text.slice(0,1400), url:href});
          }
          const tables = [...resultRoot.querySelectorAll('tr')];
          for (const tr of tables) {
            const text = tr.innerText.replace(/\s+/g,' ').trim();
            const a = tr.querySelector('a[href]');
            if (text.length > 20 && /GEM\/|bid|tender/i.test(text) && !seen.has('row'+text.slice(0,80))) {
              seen.add('row'+text.slice(0,80));
              candidates.push({title:(a?.innerText||text.split(' ').slice(0,10).join(' ')).slice(0,180),text:text.slice(0,1400),url:a?.href||''});
            }
          }
          return {url:location.href, title:document.title, filled, missing,
                  count:candidates.length, results:candidates.slice(0,80)};
        })()
        """.replace("__VALUES__", json.dumps(values, ensure_ascii=False))
        self.browser.page().runJavaScript(script, self._search_finished)

    def _search_finished(self, payload):
        self.search_btn.setEnabled(True)
        if not isinstance(payload, dict):
            self.status.setText("Could not read GeM search results. Check the page and try again.")
            QMessageBox.warning(self, "Search issue", "GeM did not return readable results. Make sure the advance-search page is loaded and try again.")
            return
        self.results = payload.get("results", [])
        keywords = self.keywords.text().strip()
        for result in self.results:
            result["score"], result["reasons"] = self._score(result, keywords)
        self.results.sort(key=lambda r: r.get("score", 0), reverse=True)
        for result in self.results:
            score = result.get("score", 0)
            title = result.get("title") or result.get("text", "Tender")[:90]
            item = QListWidgetItem(f"{score}% fit  ·  {title[:100]}")
            item.setData(Qt.ItemDataRole.UserRole, result)
            self.list.addItem(item)
        self.status.setText(
            f"GeM search finished: {len(self.results)} candidate result(s). "
            "Fit scores are keyword-based, not a guarantee of eligibility."
        )
        if not self.results:
            self.details.setPlainText(
                "No readable bid rows were detected. GeM may have changed its page layout, "
                "the selected filters may not have matched, or login/CAPTCHA may be required. "
                "Review the browser page and try a broader search."
            )
        elif self.list.count():
            self.list.setCurrentRow(0)

    def _score(self, result, keywords):
        text = (result.get("title", "") + " " + result.get("text", "")).lower()
        terms = [x.strip().lower() for x in re.split(r"[,;|]+", keywords) if x.strip()]
        if not terms:
            terms = [x.strip().lower() for x in re.split(r"[,;|]+", self.category.currentText()) if x.strip()]
        score = 35
        reasons = []
        if terms:
            matched = [t for t in terms if t in text]
            score += round(55 * len(matched) / len(terms))
            reasons.append("Keyword match: " + (", ".join(matched) if matched else "none detected"))
        else:
            score += 10
            reasons.append("Add business keywords for more useful ranking")
        if re.search(r"\b(emd exempt|no emd|emd not applicable|exempted from emd)\b", text):
            reasons.append("Possible EMD exemption wording found; verify the bid conditions")
            if "prefer emd-exempt" in getattr(self, "emd_text", "").lower():
                score += 5
        if re.search(r"\b(last date|closing date|bid end date|submission end)\b", text):
            reasons.append("A deadline label appears in the result text; confirm the actual closing date")
        return min(99, max(1, score)), reasons

    def show_details(self, row):
        if row < 0 or row >= self.list.count():
            return
        result = self.list.item(row).data(Qt.ItemDataRole.UserRole)
        reasons = result.get("reasons", [])
        body = (
            f"Fit score: {result.get('score', 0)}% (keyword-based preliminary ranking)\n\n"
            f"Title: {result.get('title') or 'Not identified'}\n\n"
            f"Result text:\n{result.get('text', '')}\n\n"
            f"Why it ranked here:\n" + "\n".join("• " + r for r in reasons) +
            "\n\nBefore applying, verify: eligibility and experience, specifications, delivery location, "
            "bid end date/time, EMD and performance security, turnover, required documents, "
            "warranty, taxes, and whether your business can fulfil the order profitably."
        )
        self.details.setPlainText(body)

    def open_selected(self):
        item = self.list.currentItem()
        if not item:
            QMessageBox.information(self, "Select a bid", "Select a result first.")
            return
        result = item.data(Qt.ItemDataRole.UserRole)
        url = result.get("url", "")
        if not url:
            QMessageBox.information(self, "No direct link", "This result has no detected bid link. Open the matching result in the GeM browser and inspect it manually.")
            return
        from PySide6.QtCore import QUrl
        self.browser.setUrl(QUrl(url))

    def review_selected(self):
        item = self.list.currentItem()
        if not item:
            QMessageBox.information(self, "Select a bid", "Search first and select a bid to review.")
            return
        result = item.data(Qt.ItemDataRole.UserRole)
        profile = {
            "business_keywords": self.keywords.text().strip(),
            "preferred_location": self.city.text().strip() or self.state.text().strip(),
            "ministry_or_buyer": self.ministry.text().strip(),
            "organisation": self.organisation.text().strip(),
            "category": self.category.currentText(),
        }
        prompt = (
            "You are a cautious Indian GeM tender screening assistant. Do not claim legal certainty. "
            "Use only the supplied result text; if information is missing, say it must be checked in the official bid document. "
            "Return: summary, business fit, red flags, missing information to verify, document checklist, "
            "commercial risks, and recommendation (SHORTLIST / REVIEW CAREFULLY / NOT ENOUGH INFORMATION). "
            "Never recommend applying based on keyword score alone.\n\nBUSINESS PROFILE:\n"
            + json.dumps(profile, ensure_ascii=False) + "\n\nBID RESULT:\n"
            + json.dumps(result, ensure_ascii=False)
        )
        self.review_btn.setEnabled(False)
        self.status.setText("Reviewing selected result with configured AI provider…")
        try:
            from ai_router import AIRouter
            self._review_prompt = prompt
            # Avoid blocking the UI while the provider responds.
            from PySide6.QtCore import QThread, Signal
            self._review_thread = _ReviewThread(prompt)
            self._review_thread.finished_text.connect(self._review_finished)
            self._review_thread.start()
        except Exception as exc:
            self.review_btn.setEnabled(True)
            self.status.setText("AI review could not start.")
            QMessageBox.warning(self, "AI review unavailable", f"{exc}\nYou can still review the result text manually.")

    def _review_finished(self, text):
        self.review_btn.setEnabled(True)
        self.status.setText("AI review complete. Verify every point in the official bid document.")
        self.details.setPlainText(self.details.toPlainText() + "\n\nAI PRELIMINARY REVIEW\n" + text)


from PySide6.QtCore import QThread, Signal


class _ReviewThread(QThread):
    finished_text = Signal(str)

    def __init__(self, prompt):
        super().__init__()
        self.prompt = prompt

    def run(self):
        try:
            from ai_router import AIRouter
            answer = AIRouter().generate(self.prompt)
        except Exception as exc:
            answer = "AI review unavailable: " + str(exc)
        self.finished_text.emit(answer)
