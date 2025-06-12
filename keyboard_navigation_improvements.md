# To-Do-Liste für Barrierefreiheit: Tastatur-Navigation

Basierend auf den WCAG 2.1.1-Richtlinien, hier sind die Schritte zur Verbesserung der Tastaturnavigation und allgemeinen Barrierefreiheit Ihrer Streamlit-Anwendung.

## 1. Semantische Struktur und Grundlegendes

- [ ] **Skip-Link einfügen**: Fügen Sie ganz am Anfang Ihrer App einen "Zum Inhalt springen"-Link ein, damit Tastaturbenutzer direkt zum Hauptbereich navigieren können.
  ```python
  import streamlit as st
  from streamlit.components.v1 import html

  # Muss als eines der ersten Elemente erscheinen
  html('<a href="#main" class="skip-link">Zum Inhalt springen</a>', height=0)
  
  # ... anderer Code ...

  # Hauptcontainer markieren
  st.markdown('<main id="main">', unsafe_allow_html=True)
  ```

- [ ] **Überschriftenhierarchie prüfen**: Stellen Sie sicher, dass `st.title`, `st.header` und `st.subheader` in einer logischen Reihenfolge verwendet werden (H1 -> H2 -> H3). Dies ist entscheidend für die Navigation mit Screen-Readern.

- [ ] **Tab-Reihenfolge kontrollieren**: Die Reihenfolge der Elemente im Code sollte der visuellen und logischen Reihenfolge in der App entsprechen. Vermeiden Sie es, das Layout nachträglich mit `st.empty()` zu verändern, da dies die Fokusreihenfolge unvorhersehbar machen kann.

## 2. Widgets und Komponenten

- [ ] **Aussagekräftige Labels verwenden**: Alle interaktiven Widgets (`st.button`, `st.selectbox`, `st.text_input` usw.) müssen klare und beschreibende Labels haben. Streamlit verwendet diese automatisch als `aria-label`.

- [ ] **Fehlende ARIA-Labels ergänzen**: Für benutzerdefinierte HTML-Komponenten oder Buttons, die nur ein Symbol haben (z.B. `»`), müssen Sie manuell ein `aria-label` hinzufügen.
  ```python
  html('<button aria-label="Nächste Seite" tabindex="0">»</button>', height=0)
  ```

- [ ] **Benutzerdefinierte Komponenten barrierefrei machen**: Wenn Sie eigene Komponenten mit `st.components.v1.declare_component` erstellen, stellen Sie sicher, dass diese:
    - [ ] Eine passende `role` haben (z.B. `role="button"`).
    - [ ] Per Tastatur fokussierbar sind (`tabIndex="0"`).
    - [ ] Auf Tastatureingaben reagieren (z.B. `onKeyDown` für "Enter").
    - [ ] Den Fokus nach einer Aktion nicht verlieren.

- [ ] **Seiten-Navigation korrekt einsetzen**: Nutzen Sie `st.navigation` für die Hauptnavigation. Dies erzeugt ein semantisch korrektes `<nav>`-Element, das von Haus aus tastaturbedienbar ist. Die Reihenfolge der Seiten in der Liste bestimmt die Tab-Reihenfolge im Menü.

## 3. Visuelles Feedback und Design

- [ ] **Sichtbare Fokus-Indikatoren sicherstellen**: Überschreiben Sie die Standard-CSS von Streamlit, um einen deutlichen und kontrastreichen Fokus-Indikator für alle fokussierbaren Elemente zu gewährleisten.
  ```python
  st.markdown("""
  <style>
  /* Macht den Fokus für alle Elemente deutlich sichtbar */
  *:focus-visible {
      outline: 3px solid var(--primary-color);
      outline-offset: 2px;
  }

  /* Style für den Skip-Link (versteckt, bis er fokussiert wird) */
  .skip-link {
      position: absolute;
      left: -10000px;
      top: auto;
      width: 1px;
      height: 1px;
      overflow: hidden;
  }
  .skip-link:focus {
      position: absolute;
      left: 1rem;
      top: 1rem;
      width: auto;
      height: auto;
      padding: 0.5rem 1rem;
      background: #ffffff;
      color: #000000;
      z-index: 9999;
  }
  </style>
  """, unsafe_allow_html=True)
  ```

- [ ] **Farbkontraste prüfen**: Überprüfen Sie, ob alle Texte und UI-Elemente einen ausreichenden Farbkontrast zum Hintergrund haben (mindestens 4.5:1 gemäß WCAG). Dies gilt auch für den Fokus-Indikator. Testen Sie dies sowohl im Light- als auch im Dark-Mode.

## 4. Testen und Audit

- [ ] **Automatisiertes Audit**: Führen Sie einen Accessibility-Scan mit den Chrome DevTools (Lighthouse-Tab) durch.
- [ ] **Semi-automatisiertes Audit**: Nutzen Sie die `axe DevTools`-Browsererweiterung, um spezifischere Probleme zu identifizieren.
- [ ] **Manuelle Tastaturprüfung**: Navigieren Sie durch die gesamte Anwendung ausschließlich mit der Tastatur.
    - [ ] **Tab**: Zum nächsten Element springen.
    - [ ] **Shift + Tab**: Zum vorherigen Element springen.
    - [ ] **Enter / Leertaste**: Buttons aktivieren und Optionen auswählen.
    - [ ] **Pfeiltasten**: Optionen in Selectboxen oder Slidern ändern.
- [ ] **Screen-Reader-Test**: Testen Sie die Anwendung mit einem Screen-Reader (z.B. NVDA für Windows, VoiceOver für macOS), um die Benutzererfahrung für sehbehinderte Personen zu überprüfen. 