"""
Security Notes Component for HTML Report.

Generates prominent security notes section displaying expert security
commentary from scan results.
"""

from typing import Dict, Any, List
from ..base_component import BaseComponent


class SecurityNotesComponent(BaseComponent):
    """Component for generating security analysis notes section."""

    def render(  # pylint: disable=arguments-differ
        self, extensions: List[Dict[str, Any]], *args, **kwargs
    ) -> str:
        """
        Render security notes section showing aggregated security commentary.

        Args:
            extensions: List of extension data dictionaries
            *args: Additional positional arguments (ignored, for compatibility)
            **kwargs: Additional keyword arguments (ignored, for compatibility)

        Returns:
            HTML string for security notes section
        """
        # Collect all unique security notes from all extensions
        all_notes = self._collect_security_notes(extensions)

        if not all_notes:
            # No security notes available - show placeholder
            return self._render_empty_notes()

        # Render notes section with all collected notes
        return self._render_notes_section(all_notes)

    def _collect_security_notes(
        self, extensions: List[Dict[str, Any]]
    ) -> List[Dict[str, str]]:
        """
        Collect all security notes from extensions with source information.

        Args:
            extensions: List of extension data

        Returns:
            List of dicts with 'note', 'extension', and 'risk_level' keys
        """
        notes = []

        for ext in extensions:
            ext_name = ext.get("display_name") or ext.get("name", "Unknown")
            security = ext.get("security", {})
            risk_level = security.get("risk_level", "unknown")
            security_notes = security.get("security_notes", [])

            # Validate security_notes is a list
            if not isinstance(security_notes, list):
                continue

            # Add each note with source information
            for note in security_notes:
                if note:  # Skip empty notes
                    notes.append(
                        {"note": note, "extension": ext_name, "risk_level": risk_level}
                    )

        return notes

    def _render_empty_notes(self) -> str:
        """Render section when no security notes are available."""
        return """
        <section class="security-notes-section">
            <h2>🛡️ Security Analysis Notes</h2>
            <p class="no-notes">No specific security concerns noted.</p>
        </section>
        """

    def _render_notes_section(self, notes: List[Dict[str, str]]) -> str:
        """
        Render security notes section with collected notes.

        Args:
            notes: List of note dictionaries with 'note', 'extension', 'risk_level'

        Returns:
            HTML string for notes section
        """
        # Generate note items
        notes_html = ""
        for note_data in notes:
            note_text = note_data["note"]
            extension = note_data["extension"]
            risk_level = note_data["risk_level"]

            # Determine risk class for styling
            risk_class = (
                risk_level
                if risk_level in ["low", "medium", "high", "critical"]
                else "unknown"
            )

            notes_html += f"""
            <li class="note-item">
                <div class="note-content">
                    <span class="note-text">{self._safe_escape(note_text)}</span>
                    <span class="note-source">
                        <span class="extension-name">{self._safe_escape(extension)}</span>
                        <span class="risk-badge risk-{risk_class}">{risk_level.upper()}</span>
                    </span>
                </div>
            </li>
            """

        return f"""
        <section class="security-notes-section">
            <h2>🛡️ Security Analysis Notes</h2>
            <div class="notes-container">
                <p class="notes-description">
                    Expert security commentary highlighting key concerns and observations from the analysis.
                </p>
                <ul class="notes-list">
                    {notes_html}
                </ul>
            </div>
        </section>
        """
