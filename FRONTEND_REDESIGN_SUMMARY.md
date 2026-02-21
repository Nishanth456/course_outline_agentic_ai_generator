# Frontend Layout Redesign Summary

## Changes Made

### 1. **Left Sidebar - Fixed Input Form**
   - All user inputs moved to the **left sidebar**
   - Form elements remain **fixed/sticky** while user scrolls through output
   - Inputs include:
     - Course Title
     - Duration (hours)
     - Course Description
     - Audience Level
     - Audience Background
     - Learning Mode
     - Depth Requirement
     - Custom Constraints
     - **PDF Upload (now integrated in form)**

### 2. **PDF Upload - Integrated Before Generate Button**
   - PDF upload moved from **separate section** to **inside the form**
   - Appears under "📄 Reference Material" section
   - User can upload PDF **before clicking "Generate Outline"**
   - No more waiting for generation to see upload option
   - Success message shows immediately after upload

### 3. **Generate Outline Button**
   - Located at the bottom of the sidebar form
   - User completes all inputs (including optional PDF) → clicks button
   - Triggers course generation immediately

### 4. **Main Content Area - Output Only**
   - Right side shows **course outline only**
   - Full page width dedicated to output
   - Output is **scrollable** independently
   - Sidebar stays fixed while scrolling through output

### 5. **Controls Section**
   - Moved to **bottom of sidebar** (below the form)
   - Contains:
     - 🔄 Reset Session button
     - Debug Mode toggle
     - Session info (when debug enabled)

## User Flow

### Before (Old Layout)
```
┌─ Sidebar ─┐
│  Debug    │
│  Session  │
└───────────┘
        ↓
┌─── MAIN CONTENT ────┐
│ LEFT       │ RIGHT  │
│ FORM       │OUTPUT  │
│ PDF        │        │
│ GENERATE   │        │
└────────────┴────────┘
```

### After (New Layout)
```
┌──── SIDEBAR (FIXED) ────┐  ┌─── MAIN CONTENT (SCROLLABLE) ───┐
│                         │  │                                   │
│ 📝 Course Details       │  │                                   │
│ • Title                 │  │ 📖 Generated Outline              │
│ • Duration              │  │ • Summary                         │
│ • Description           │  │ • Modules (with expanders)        │
│ • Audience Level        │  │ • Capstone Project                │
│ • Audience Category     │  │ • Tools & Resources               │
│ • Learning Mode         │  │ • Instructor Notes                │
│ • Depth                 │  │                                   │
│ • Constraints           │  │  (scrolls down, sidebar stays)    │
│                         │  │                                   │
│ 📄 Reference Material   │  │                                   │
│ [PDF Upload Input]      │  │                                   │
│                         │  │                                   │
│ [✨ Generate Outline]   │  │                                   │
│                         │  │                                   │
│ ────────────────────── │  │                                   │
│ ⚙️ Controls             │  │                                   │
│ [🔄 Reset Session]      │  │                                   │
│ [☑ Debug Mode]          │  │                                   │
│                         │  │                                   │
└─────────────────────────┘  └───────────────────────────────────┘
```

## Key Benefits

1. ✅ **Better Organization** - All inputs grouped in sidebar, output focused in main area
2. ✅ **Fixed Sidebar** - Form always visible while scrolling output
3. ✅ **Intuitive PDF Upload** - User uploads BEFORE generating (not after)
4. ✅ **More Output Space** - Full width for course outline
5. ✅ **Cleaner UX** - No form elements cluttering the output view
6. ✅ **Responsive** - Left sidebar stays fixed, right content scrolls

## Implementation Details

### Modified Files
- `app.py` - Main Streamlit application

### Key Function Changes

#### `render_input_form()`
- **Before:** Returned `UserInputSchema` only
- **After:** Returns tuple `(UserInputSchema, pdf_path)` 
- Now renders inside `st.sidebar`
- Integrates PDF upload within the form
- Returns both user input and PDF path after form submission

#### `render_pdf_upload()` 
- **Before:** Separate function showing PDF upload in main area
- **After:** Removed - PDF upload integrated into `render_input_form()`

#### `render_sidebar_controls()`
- **Before:** Called in main flow
- **After:** Rendered separately after form for controls section
- Groups debug/reset controls at bottom of sidebar

#### `main()`
- **Before:** Two-column layout with form on left, output on right
- **After:** Sidebar for input, full main area for output
- Simplified flow: render sidebar form → sidebar controls → main content

### Sidebar Configuration
```python
st.set_page_config(
    page_title="Course AI Agent",
    page_icon="📚",
    layout="wide",          # Full width layout
    initial_sidebar_state="collapsed"  # Sidebar can be toggled
)
```

## Browser Behavior

### Sidebar
- Fixed position (doesn't scroll)
- User scrolls to see all form fields
- Form stays visible while scrolling output

### Main Content Area
- Independent scrollbar
- Scrolls separately from sidebar
- Full page width for output

### Responsive Design
- Sidebar auto-collapses on small screens (mobile)
- Layout adapts automatically

## Data Flow

```
User Input (Sidebar) 
    ↓
PDF Upload (Sidebar)
    ↓
Click "Generate Outline" (Sidebar)
    ↓
render_input_form() returns (UserInputSchema, pdf_path)
    ↓
main() processes and generates outline
    ↓
render_output_panel() displays in main area
    ↓
User scrolls through outline (sidebar stays fixed)
```

## Testing Checklist

- [x] Syntax validation: Python code compiles
- [ ] Run Streamlit app: `streamlit run app.py`
- [ ] Test form input on sidebar
- [ ] Test PDF upload (before generate)
- [ ] Test scrolling behavior
- [ ] Verify sidebar stays fixed while scrolling
- [ ] Test reset button
- [ ] Test debug mode toggle
- [ ] Test session persistence
- [ ] Screen at different window sizes

## Next Steps

To test the updated layout:

```bash
cd c:\Users\nisha\Projects\tcs_ai\course_ai_agent
streamlit run app.py
```

The app will:
1. Show sidebar with all form inputs
2. Allow PDF upload in the form
3. Show "Generate Outline" button
4. Display output in main scrollable area
5. Keep sidebar fixed while output scrolls
