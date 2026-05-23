"""
WindBrowser - WindOS Web Tarayıcısı
PyQt5 + PyQtWebEngine | Karanlık Fütüristik Tema
"""

import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLineEdit, QPushButton, QTabWidget,
    QTabBar, QStatusBar, QLabel, QFrame, QSizePolicy,
    QToolButton, QProgressBar, QShortcut
)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtCore import Qt, QUrl, QSize
from PyQt5.QtGui import QIcon, QFont, QColor, QPalette, QKeySequence

# ── Renk Paleti ───────────────────────────────────────────────────────────────
STYLE = """
QMainWindow, QWidget {
    background-color: #1A1C22;
    color: #DCDDE0;
}

/* Üst toolbar */
#toolbar {
    background-color: #13151A;
    border-bottom: 1px solid #2E3140;
    padding: 4px 6px;
}

/* URL çubuğu */
#urlbar {
    background-color: #22252E;
    border: 1px solid #2E3140;
    border-radius: 20px;
    color: #E0E2E8;
    font-size: 13px;
    padding: 6px 16px;
    selection-background-color: #0078D4;
}
#urlbar:focus {
    border: 1px solid #0078D4;
    background-color: #262930;
}

/* Nav butonları */
#navbtn {
    background-color: transparent;
    border: none;
    border-radius: 6px;
    color: #8899A6;
    font-size: 18px;
    font-weight: bold;
    min-width: 36px;
    min-height: 36px;
    padding: 0px;
}
#navbtn:hover  { background-color: #2A2D38; color: #E0E2E8; }
#navbtn:pressed{ background-color: #1E2128; }
#navbtn:disabled{ color: #3A3D48; }

/* Yeni sekme butonu */
#newtabbtn {
    background-color: transparent;
    border: none;
    border-radius: 6px;
    color: #0078D4;
    font-size: 20px;
    min-width: 30px;
    min-height: 30px;
}
#newtabbtn:hover { background-color: #1E2840; }

/* Sekme çubuğu */
QTabWidget::pane {
    border: none;
    background-color: #1A1C22;
}
QTabBar {
    background-color: #13151A;
}
QTabBar::tab {
    background-color: #1E2128;
    color: #8899A6;
    border: none;
    border-right: 1px solid #2E3140;
    padding: 8px 36px 8px 14px;
    font-size: 12px;
    min-width: 140px;
    max-width: 220px;
}
QTabBar::tab:selected {
    background-color: #1A1C22;
    color: #E0E2E8;
    border-top: 2px solid #0078D4;
}
QTabBar::tab:hover:!selected {
    background-color: #22252E;
    color: #C0C4CC;
}
QTabBar::close-button {
    image: none;
    subcontrol-position: right;
}

/* Progress bar */
QProgressBar {
    background-color: transparent;
    border: none;
    height: 2px;
    text-align: center;
    color: transparent;
}
QProgressBar::chunk {
    background-color: #0078D4;
    border-radius: 1px;
}

/* Durum çubuğu */
QStatusBar {
    background-color: #13151A;
    color: #5A6A7A;
    font-size: 11px;
    border-top: 1px solid #2E3140;
}
QStatusBar::item { border: none; }

/* Ayırıcı çizgi */
QFrame[frameShape="4"], QFrame[frameShape="5"] {
    color: #2E3140;
}

/* Scrollbar */
QScrollBar:vertical {
    background: #1A1C22;
    width: 8px;
    border: none;
}
QScrollBar::handle:vertical {
    background: #3A3D48;
    border-radius: 4px;
    min-height: 20px;
}
QScrollBar::handle:vertical:hover { background: #0078D4; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

/* Menü */
QMenu {
    background-color: #22252E;
    border: 1px solid #2E3140;
    border-radius: 6px;
    color: #DCDDE0;
    padding: 4px;
}
QMenu::item { padding: 6px 20px; border-radius: 4px; }
QMenu::item:selected { background-color: #1E2840; color: #0078D4; }
"""

HOME_URL = "https://www.google.com"


# ── Özel WebEnginePage: yeni sekme yönlendirmesi ────────────────────────────
class WindPage(QWebEnginePage):
    def __init__(self, browser_view, parent=None):
        super().__init__(parent)
        self._browser_view = browser_view

    def createWindow(self, _type):
        return self._browser_view.main_window.new_tab().page()


# ── Tarayıcı Sekmesi ─────────────────────────────────────────────────────────
class BrowserTab(QWebEngineView):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setPage(WindPage(self, self))
        self.load(QUrl(HOME_URL))

        self.titleChanged.connect(self._on_title_changed)
        self.loadStarted.connect(self._on_load_started)
        self.loadProgress.connect(self._on_load_progress)
        self.loadFinished.connect(self._on_load_finished)
        self.urlChanged.connect(self._on_url_changed)

    def _tab_index(self):
        tabs = self.main_window.tabs
        for i in range(tabs.count()):
            if tabs.widget(i) is self:
                return i
        return -1

    def _on_title_changed(self, title):
        i = self._tab_index()
        if i >= 0:
            short = (title[:20] + "…") if len(title) > 22 else title
            self.main_window.tabs.setTabText(i, short or "Yeni Sekme")
            if self.main_window.tabs.currentIndex() == i:
                self.main_window.setWindowTitle(f"{title} — WindBrowser")

    def _on_load_started(self):
        if self.main_window.tabs.currentWidget() is self:
            self.main_window.progress.show()
            self.main_window.progress.setValue(0)

    def _on_load_progress(self, p):
        if self.main_window.tabs.currentWidget() is self:
            self.main_window.progress.setValue(p)

    def _on_load_finished(self, ok):
        if self.main_window.tabs.currentWidget() is self:
            self.main_window.progress.setValue(100)
            self.main_window.progress.hide()
            self.main_window.refresh_nav_state()
        if not ok:
            i = self._tab_index()
            if i >= 0:
                self.main_window.tabs.setTabText(i, "Hata")

    def _on_url_changed(self, url):
        if self.main_window.tabs.currentWidget() is self:
            self.main_window.urlbar.setText(url.toString())
            self.main_window.status.showMessage(url.toString(), 3000)


# ── Ana Pencere ───────────────────────────────────────────────────────────────
class WindBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WindBrowser — WindOS")
        self.setMinimumSize(900, 620)
        self.resize(1200, 780)
        self._build_ui()
        self._setup_shortcuts()

    # ── UI Yapısı ────────────────────────────────────────────────────────────
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Toolbar
        toolbar = QWidget(objectName="toolbar")
        tb_lay = QHBoxLayout(toolbar)
        tb_lay.setContentsMargins(8, 4, 8, 4)
        tb_lay.setSpacing(4)
        root.addWidget(toolbar)

        # İleri/Geri/Yenile
        self.btn_back = self._nav_btn("◀", "Geri (Alt+Sol)")
        self.btn_fwd  = self._nav_btn("▶", "İleri (Alt+Sağ)")
        self.btn_reload = self._nav_btn("↺", "Yenile (F5)")
        self.btn_home   = self._nav_btn("⌂", "Ana Sayfa")

        for b in (self.btn_back, self.btn_fwd, self.btn_reload, self.btn_home):
            tb_lay.addWidget(b)

        sep1 = QFrame(); sep1.setFrameShape(QFrame.VLine)
        tb_lay.addWidget(sep1)

        # URL çubuğu
        self.urlbar = QLineEdit(objectName="urlbar")
        self.urlbar.setPlaceholderText("Adres girin veya arama yapın…")
        self.urlbar.returnPressed.connect(self._navigate)
        self.urlbar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.urlbar.setFixedHeight(36)
        tb_lay.addWidget(self.urlbar)

        # Yeni sekme
        btn_new = QToolButton(objectName="newtabbtn", text="+")
        btn_new.setFixedSize(32, 32)
        btn_new.clicked.connect(self.new_tab)
        tb_lay.addWidget(btn_new)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setFixedHeight(2)
        self.progress.setTextVisible(False)
        self.progress.hide()
        root.addWidget(self.progress)

        # Sekmeler
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.setDocumentMode(True)
        self.tabs.tabCloseRequested.connect(self._close_tab)
        self.tabs.currentChanged.connect(self._tab_changed)
        root.addWidget(self.tabs)

        # Status bar
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        ver = QLabel("WindBrowser v1.0  |  WindOS")
        ver.setStyleSheet("color: #3A4A5A; font-size: 10px; padding-right: 6px;")
        self.status.addPermanentWidget(ver)

        # Buton bağlantıları
        self.btn_back.clicked.connect(lambda: self.current_tab().back())
        self.btn_fwd.clicked.connect(lambda: self.current_tab().forward())
        self.btn_reload.clicked.connect(self._reload_or_stop)
        self.btn_home.clicked.connect(lambda: self.current_tab().load(QUrl(HOME_URL)))

        # İlk sekme
        self.new_tab()

    def _nav_btn(self, text, tip):
        b = QPushButton(text, objectName="navbtn")
        b.setFixedSize(36, 36)
        b.setToolTip(tip)
        return b

    # ── Kısayollar ───────────────────────────────────────────────────────────
    def _setup_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+T"),  self, self.new_tab)
        QShortcut(QKeySequence("Ctrl+W"),  self, self._close_current_tab)
        QShortcut(QKeySequence("Ctrl+L"),  self, self.urlbar.setFocus)
        QShortcut(QKeySequence("F5"),      self, self._reload_or_stop)
        QShortcut(QKeySequence("Alt+Left"),  self, lambda: self.current_tab().back())
        QShortcut(QKeySequence("Alt+Right"), self, lambda: self.current_tab().forward())
        QShortcut(QKeySequence("Ctrl+Tab"), self, self._next_tab)
        QShortcut(QKeySequence("Escape"),   self, self._stop_or_blur)

    # ── Sekme Yönetimi ────────────────────────────────────────────────────────
    def new_tab(self, url=None):
        tab = BrowserTab(self)
        if url:
            tab.load(QUrl(url))
        i = self.tabs.addTab(tab, "Yeni Sekme")
        self.tabs.setCurrentIndex(i)
        self.urlbar.setFocus()
        return tab

    def _close_tab(self, i):
        if self.tabs.count() > 1:
            widget = self.tabs.widget(i)
            self.tabs.removeTab(i)
            widget.deleteLater()
        else:
            self.close()

    def _close_current_tab(self):
        self._close_tab(self.tabs.currentIndex())

    def _tab_changed(self, i):
        tab = self.tabs.widget(i)
        if tab:
            self.urlbar.setText(tab.url().toString())
            self.setWindowTitle(f"{tab.title() or 'WindBrowser'} — WindBrowser")
            self.refresh_nav_state()

    def _next_tab(self):
        n = self.tabs.count()
        if n > 1:
            self.tabs.setCurrentIndex((self.tabs.currentIndex() + 1) % n)

    # ── Navigasyon ────────────────────────────────────────────────────────────
    def current_tab(self) -> BrowserTab:
        return self.tabs.currentWidget()

    def _navigate(self):
        raw = self.urlbar.text().strip()
        if not raw:
            return
        if "." in raw and " " not in raw and not raw.startswith("http"):
            url = QUrl("https://" + raw)
        elif raw.startswith(("http://", "https://", "file://", "ftp://")):
            url = QUrl(raw)
        else:
            # Arama motoruna yönlendir
            url = QUrl("https://www.google.com/search?q=" + raw.replace(" ", "+"))
        self.current_tab().load(url)

    def _reload_or_stop(self):
        tab = self.current_tab()
        if tab.page().isLoading() if hasattr(tab.page(), "isLoading") else False:
            tab.stop()
        else:
            tab.reload()

    def _stop_or_blur(self):
        tab = self.current_tab()
        tab.stop()
        self.urlbar.clearFocus()

    def refresh_nav_state(self):
        tab = self.current_tab()
        if tab:
            self.btn_back.setEnabled(tab.history().canGoBack())
            self.btn_fwd.setEnabled(tab.history().canGoForward())


# ── Giriş Noktası ─────────────────────────────────────────────────────────────
def main():
    # HiDPI desteği
    try:
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    except AttributeError:
        pass

    app = QApplication(sys.argv)
    app.setApplicationName("WindBrowser")
    app.setOrganizationName("WindOS")
    app.setStyleSheet(STYLE)

    # Varsayılan font
    font = QFont("Segoe UI", 10)
    font.setHintingPreference(QFont.PreferFullHinting)
    app.setFont(font)

    window = WindBrowser()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
