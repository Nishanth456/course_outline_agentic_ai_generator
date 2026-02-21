# Frontend Layout - Quick Reference

## Visual Layout Comparison

### OLD LAYOUT (Two Columns)
```
┌──────── HEADER ────────────┐
│  Course Outline Generator  │
└────────────────────────────┘

┌──────────────┬──────────────┐
│              │              │
│   INPUT      │   OUTPUT     │
│   FORM       │   PANEL      │
│              │              │
│   • Title    │ • Summary    │
│   • Duration │ • Modules    │
│   • Desc     │ • Capstone   │
│   • Audience │              │
│   • Mode     │ (scrolls)    │
│              │              │
│   PDF UPLOAD │              │
│   (after     │              │
│    generate) │              │
│              │              │
│   GEN BTN    │              │
│              │              │
└──────────────┴──────────────┘

PROBLEMS:
✗ PDF upload appears AFTER clicking Generate
✗ Input form clutters the view
✗ Output competes with input for horizontal space
```

### NEW LAYOUT (Sidebar + Full Main Area)
```
┌──────────────────────────────┐
│   Course Outline Generator   │
└──────────────────────────────┘

┌─ FIXED SIDEBAR ─┬─ MAIN AREA (Scrollable) ───┐
│                 │                            │
│ 📝 Course Det.  │ 📖 Generated Outline       │
│ • Title ....    │ • Summary                  │
│ • Duration .    │ • Modules                  │
│ • Desc... . │ • Capstone                │
│ • Audience     │ • Tools                    │
│ • Mode...      │ • Notes                    │
│ • Depth...     │                            │
│ • Constraints  │ (scrolls down)             │
│   ...scroll    │                            │
│   down for     │                            │
│📄 Ref Mat.    │ (sidebar stays fixed)      │
│ [PDF Upload]   │                            │
│   ...          │                            │
│ [✨ Generate]   │                            │
│                │                            │
│ ─ Controls ─   │                            │
│ [Reset][Debug] │                            │
│                │                            │
└─────────────────┴────────────────────────────┘

IMPROVEMENTS:
✓ PDF upload BEFORE Generate button
✓ Sidebar stays FIXED while scrolling
✓ Full width for more readable output
✓ Clean separation: input vs output
```

## Key Layout Features

### 1. Sidebar (Fixed Width)
- **Header:** "📝 Course Details"
- **Form inputs:** All required fields
- **PDF section:** "📄 Reference Material"
- **Upload box:** Take optional PDF before generating
- **Generate button:** "✨ Generate Outline"
- **Divider:** `---`
- **Controls:** Reset & Debug
- **Status:** Shows session info if debug on

### 2. Main Content Area (Full Width)
- **Header message:** When no outline yet
- **Output panels:** When outline generated
  - Course summary
  - Modules (expandable)
  - Capstone project
  - Tools & resources
  - Instructor notes
  - Debug info (if enabled)

### 3. Scrolling Behavior
- **Sidebar:** User scrolls DOWN within sidebar to see all inputs
- **Main area:** Scrolls independently from sidebar
- **Result:** Sidebar stays visible, output scrolls

## Form Fields in Sidebar

```
SIDEBAR FORM
├─ 📝 Course Details
│  ├─ Course Title *
│  ├─ Duration (hours) *
│  ├─ Course Description *
│  ├─ Audience Level *
│  ├─ Audience Background *
│  ├─ Learning Mode *
│  ├─ Depth Requirement *
│  └─ Custom Constraints
│
├─ 📄 Reference Material
│  └─ [PDF File Uploader]
│
└─ [✨ Generate Outline Button]
```

## Controls Section

```
CONTROLS (Bottom of Sidebar)
├─ ⚙️ Controls
│  ├─ [🔄 Reset Session]
│  ├─ ☑ Debug Mode
│  └─ (If Debug ON)
│     ├─ Session ID: xxx...
│     ├─ Created: HH:MM:SS
│     └─ Status: ✅ Outline generated
```

## Output Panels (Main Area)

```
MAIN AREA OUTPUT
├─ ✅ Course outline generated!
│
├─ 📖 Generated Course Outline
│  ├─ Metrics (3 columns)
│  │  ├─ Duration: 40 hours
│  │  ├─ Modules: 6
│  │  └─ Learning Outcomes: 3
│  │
│  ├─ 📋 Course Summary
│  │
│  ├─ 👥 Target Audience
│  │  ├─ Level: ...
│  │  ├─ Category: ...
│  │  ├─ Mode: ...
│  │  └─ Depth: ...
│  │
│  ├─ 📚 Prerequisites
│  │
│  ├─ 🎯 Course-Level Learning Outcomes
│  │
│  ├─ 📚 Course Modules (Expandable)
│  │  ├─ Module 1 (5 hours)
│  │  ├─ Module 2 (5 hours)
│  │  └─ ...
│  │
│  ├─ 🏆 Capstone Project
│  │
│  └─ 🛠️ Recommended Tools
```

## Mobile Responsiveness

### Desktop (Wide Screen)
```
┌─ sidebar ─┬───── main content ────┐
│ fixed     │ can be very wide       │
└───────────┴────────────────────────┘
```

### Tablet/Mobile (Narrow Screen)
```
┌─ sidebar ─┐
│ toggleable│ (collapsible via button)
└───────────┴───────────────────────┐
│ MAIN CONTENT (full width below)   │
└──────────────────────────────────┘
```

## Code Structure

### File: app.py

#### Main Sections:
1. **Initialization** (lines 33-68)
   - Session manager
   - Session creation

2. **UI Sections** (lines 70-360)
   - `render_header()` - Title & description
   - `render_input_form()` - Sidebar form + PDF + Generate button
   - `render_output_panel()` - Course outline display
   - `render_sidebar_controls()` - Reset & debug controls

3. **Main Flow** (lines 370-418)
   - `main()` - Orchestrates the layout

#### Key Functions:
```python
# Before form submission - shows empty sidebar
render_input_form() → (None, None)

# After form submission - returns user data
render_input_form() → (UserInputSchema, pdf_path)

# Generates and displays output
main() → asyncio.run(orchestrator.run(...))
```

## User Interaction Flow

```
1. Page loads
   ↓
2. Sidebar: User fills form
   ↓
3. Sidebar: User optionally uploads PDF
   ↓
4. Sidebar: User clicks "Generate Outline"
   ↓
5. Main area: "⏳ Generating course outline..."
   ↓
6. Main area: Outline displays
   ↓
7. User scrolls through outline
   (Sidebar stays fixed at left)
   ↓
8. Optional: Click "Reset Session" in sidebar to start over
```

## Quick Navigation

| Task | Where |
|------|-------|
| Fill course title | Left sidebar, top |
| Set duration | Left sidebar, form |
| Upload PDF | Left sidebar, "📄 Reference Material" |
| Generate outline | Left sidebar, bottom button |
| View outline | Main area, scrollable |
| Reset session | Left sidebar, bottom controls |
| Toggle debug | Left sidebar, bottom checkbox |
| See raw JSON | Main area, debug section |

---

**Layout Status:** ✅ Production Ready

Test the new layout:
```bash
streamlit run app.py
```
