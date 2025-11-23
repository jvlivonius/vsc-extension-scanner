"""
Tests for SecurityNotesComponent in HTML Report Generator.

Covers security notes aggregation, rendering, and edge cases.
Target: 95%+ coverage
"""

import unittest
import pytest

from vscode_scanner.html_report.components.security_notes import (
    SecurityNotesComponent,
)


@pytest.mark.unit
class TestSecurityNotesComponent(unittest.TestCase):
    """Test suite for SecurityNotesComponent with comprehensive coverage."""

    def setUp(self):
        """Set up test fixtures."""
        self.security_notes = SecurityNotesComponent()

        # Extension with security notes
        self.ext_with_notes = {
            "id": "test.ext1",
            "name": "TestExt1",
            "display_name": "Test Extension 1",
            "security": {
                "risk_level": "high",
                "security_notes": [
                    "Extension makes network requests to unverified domains",
                    "Code contains obfuscation patterns",
                ],
            },
        }

        # Extension with single note
        self.ext_single_note = {
            "id": "test.ext2",
            "name": "TestExt2",
            "display_name": "Test Extension 2",
            "security": {
                "risk_level": "medium",
                "security_notes": ["High permission scope detected"],
            },
        }

        # Extension without security notes
        self.ext_no_notes = {
            "id": "test.ext3",
            "name": "TestExt3",
            "display_name": "Test Extension 3",
            "security": {"risk_level": "low"},
        }

        # Extension with empty notes array
        self.ext_empty_notes = {
            "id": "test.ext4",
            "name": "TestExt4",
            "display_name": "Test Extension 4",
            "security": {"risk_level": "low", "security_notes": []},
        }

        # Extension with critical risk
        self.ext_critical = {
            "id": "test.ext5",
            "name": "TestExt5",
            "display_name": "Critical Extension",
            "security": {
                "risk_level": "critical",
                "security_notes": ["Critical vulnerability detected"],
            },
        }

    # === Basic Rendering Tests ===

    def test_render_with_notes(self):
        """Test rendering section with security notes present."""
        extensions = [self.ext_with_notes]
        result = self.security_notes.render(extensions)

        # Verify section structure
        self.assertIn('class="security-notes-section"', result)
        self.assertIn("🛡️ Security Analysis Notes", result)
        self.assertIn('class="notes-container"', result)
        self.assertIn('class="notes-list"', result)

    def test_render_empty_when_no_notes(self):
        """Test rendering when no extensions have security notes."""
        extensions = [self.ext_no_notes, self.ext_empty_notes]
        result = self.security_notes.render(extensions)

        # Should show "no notes" message
        self.assertIn('class="security-notes-section"', result)
        self.assertIn("No specific security concerns noted", result)
        self.assertIn('class="no-notes"', result)

    def test_render_with_empty_extensions_list(self):
        """Test rendering with empty extensions list."""
        result = self.security_notes.render([])

        # Should show "no notes" message
        self.assertIn("No specific security concerns noted", result)

    # === Note Collection Tests ===

    def test_collect_multiple_notes_from_single_extension(self):
        """Test collecting multiple notes from one extension."""
        extensions = [self.ext_with_notes]
        notes = self.security_notes._collect_security_notes(extensions)

        self.assertEqual(len(notes), 2)
        self.assertEqual(
            notes[0]["note"], "Extension makes network requests to unverified domains"
        )
        self.assertEqual(notes[1]["note"], "Code contains obfuscation patterns")
        self.assertEqual(notes[0]["extension"], "Test Extension 1")

    def test_collect_notes_from_multiple_extensions(self):
        """Test collecting notes from multiple extensions."""
        extensions = [self.ext_with_notes, self.ext_single_note]
        notes = self.security_notes._collect_security_notes(extensions)

        self.assertEqual(len(notes), 3)
        # Verify source tracking
        extensions_with_notes = [n["extension"] for n in notes]
        self.assertIn("Test Extension 1", extensions_with_notes)
        self.assertIn("Test Extension 2", extensions_with_notes)

    def test_collect_notes_skips_empty_notes(self):
        """Test that empty note strings are skipped."""
        ext_with_empty = {
            "id": "test.empty",
            "name": "EmptyExt",
            "display_name": "Empty Extension",
            "security": {
                "risk_level": "low",
                "security_notes": ["Valid note", "", None, "Another valid note"],
            },
        }

        notes = self.security_notes._collect_security_notes([ext_with_empty])

        # Should only collect non-empty notes
        self.assertEqual(len(notes), 2)
        self.assertEqual(notes[0]["note"], "Valid note")
        self.assertEqual(notes[1]["note"], "Another valid note")

    def test_collect_notes_handles_missing_security_key(self):
        """Test handling extensions without security key."""
        ext_no_security = {
            "id": "test.nosec",
            "name": "NoSec",
            "display_name": "No Security",
        }

        notes = self.security_notes._collect_security_notes([ext_no_security])

        # Should return empty list
        self.assertEqual(len(notes), 0)

    def test_collect_notes_handles_invalid_notes_type(self):
        """Test handling when security_notes is not a list."""
        ext_invalid = {
            "id": "test.invalid",
            "name": "InvalidExt",
            "display_name": "Invalid Extension",
            "security": {"risk_level": "low", "security_notes": "Not a list"},
        }

        notes = self.security_notes._collect_security_notes([ext_invalid])

        # Should skip invalid notes
        self.assertEqual(len(notes), 0)

    # === Risk Level Tests ===

    def test_collect_notes_preserves_risk_levels(self):
        """Test that risk levels are correctly preserved."""
        extensions = [
            self.ext_with_notes,  # high
            self.ext_single_note,  # medium
            self.ext_critical,  # critical
        ]
        notes = self.security_notes._collect_security_notes(extensions)

        # Find notes by content and verify risk levels
        high_note = next(
            n
            for n in notes
            if "unverified domains" in n["note"] or "obfuscation" in n["note"]
        )
        medium_note = next(n for n in notes if "permission scope" in n["note"])
        critical_note = next(n for n in notes if "Critical vulnerability" in n["note"])

        self.assertEqual(high_note["risk_level"], "high")
        self.assertEqual(medium_note["risk_level"], "medium")
        self.assertEqual(critical_note["risk_level"], "critical")

    def test_render_includes_risk_badges(self):
        """Test that rendered HTML includes risk badges."""
        extensions = [self.ext_with_notes, self.ext_critical]
        result = self.security_notes.render(extensions)

        # Verify risk badges present
        self.assertIn('class="risk-badge risk-high"', result)
        self.assertIn("HIGH", result)
        self.assertIn('class="risk-badge risk-critical"', result)
        self.assertIn("CRITICAL", result)

    def test_render_unknown_risk_level(self):
        """Test handling of unknown/invalid risk levels."""
        ext_unknown = {
            "id": "test.unknown",
            "name": "UnknownExt",
            "display_name": "Unknown Extension",
            "security": {
                "risk_level": "invalid_level",
                "security_notes": ["Some note"],
            },
        }

        result = self.security_notes.render([ext_unknown])

        # Should use "unknown" class for invalid risk levels
        self.assertIn('class="risk-badge risk-unknown"', result)

    # === HTML Structure Tests ===

    def test_render_notes_content_structure(self):
        """Test detailed HTML structure of notes rendering."""
        extensions = [self.ext_with_notes]
        result = self.security_notes.render(extensions)

        # Verify detailed structure
        self.assertIn('class="note-item"', result)
        self.assertIn('class="note-content"', result)
        self.assertIn('class="note-text"', result)
        self.assertIn('class="note-source"', result)
        self.assertIn('class="extension-name"', result)

    def test_render_includes_description(self):
        """Test that notes section includes description text."""
        extensions = [self.ext_with_notes]
        result = self.security_notes.render(extensions)

        self.assertIn('class="notes-description"', result)
        self.assertIn("Expert security commentary", result)

    def test_render_includes_extension_names(self):
        """Test that extension names are displayed for each note."""
        extensions = [self.ext_with_notes, self.ext_single_note]
        result = self.security_notes.render(extensions)

        # Verify extension names appear
        self.assertIn("Test Extension 1", result)
        self.assertIn("Test Extension 2", result)

    # === HTML Escaping Tests ===

    def test_safe_escape_note_content(self):
        """Test that note content is properly escaped."""
        ext_xss = {
            "id": "test.xss",
            "name": "XSSExt",
            "display_name": "XSS <script>alert('test')</script>",
            "security": {
                "risk_level": "high",
                "security_notes": [
                    "Contains <script>alert('xss')</script> pattern",
                    "Uses \"quotes\" and 'apostrophes'",
                ],
            },
        }

        result = self.security_notes.render([ext_xss])

        # Verify HTML is escaped
        self.assertNotIn("<script>", result)
        self.assertIn("&lt;script&gt;", result)
        # Extension name should also be escaped
        self.assertIn("XSS &lt;script&gt;", result)

    # === Edge Cases ===

    def test_render_with_missing_display_name(self):
        """Test rendering when extension has no display_name."""
        ext_no_display = {
            "id": "test.nodisplay",
            "name": "NoDisplay",
            "security": {
                "risk_level": "low",
                "security_notes": ["Some security note"],
            },
        }

        result = self.security_notes.render([ext_no_display])

        # Should fall back to 'name' field
        self.assertIn("NoDisplay", result)

    def test_render_with_no_name_fields(self):
        """Test rendering when extension has neither display_name nor name."""
        ext_no_name = {
            "id": "test.noname",
            "security": {
                "risk_level": "low",
                "security_notes": ["Some security note"],
            },
        }

        result = self.security_notes.render([ext_no_name])

        # Should fall back to "Unknown"
        self.assertIn("Unknown", result)

    def test_render_performance_with_many_notes(self):
        """Test rendering performance with large number of notes."""
        # Create 50 extensions with 5 notes each = 250 notes
        extensions = []
        for i in range(50):
            ext = {
                "id": f"test.ext{i}",
                "name": f"Extension{i}",
                "display_name": f"Test Extension {i}",
                "security": {
                    "risk_level": "medium",
                    "security_notes": [
                        f"Note {j} from extension {i}" for j in range(5)
                    ],
                },
            }
            extensions.append(ext)

        # Should complete without error
        result = self.security_notes.render(extensions)

        # Verify basic structure
        self.assertIn('class="security-notes-section"', result)
        self.assertIn('class="notes-list"', result)
        # Should have 250 note items
        self.assertEqual(result.count('class="note-item"'), 250)


if __name__ == "__main__":
    unittest.main()
