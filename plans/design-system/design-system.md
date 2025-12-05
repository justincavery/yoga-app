# YogaFlow Design System

**Version:** 1.0
**Last Updated:** 2025-12-05
**Status:** Initial Release

---

## Design Principles

### Core Values
- **Minimalist and Calming:** Use whitespace effectively, peaceful color palette
- **Visual Focus:** Large, clear images of poses as primary visual elements
- **Intuitive Navigation:** Clear hierarchy, consistent patterns
- **Mobile-First:** Design for mobile experience first, then scale up
- **Accessible:** High contrast, readable fonts, WCAG 2.1 AA compliant

---

## Color Palette

### Primary Colors

```css
/* Primary - Calming Blue */
--color-primary-50: #E3F2FD;
--color-primary-100: #BBDEFB;
--color-primary-200: #90CAF9;
--color-primary-300: #64B5F6;
--color-primary-400: #42A5F5;
--color-primary-500: #4A90E2;  /* Main primary */
--color-primary-600: #1E88E5;
--color-primary-700: #1976D2;
--color-primary-800: #1565C0;
--color-primary-900: #0D47A1;
```

### Secondary Colors

```css
/* Secondary - Earthy Green */
--color-secondary-50: #F1F8E9;
--color-secondary-100: #DCEDC8;
--color-secondary-200: #C5E1A5;
--color-secondary-300: #AED581;
--color-secondary-400: #9CCC65;
--color-secondary-500: #7CB342;  /* Main secondary */
--color-secondary-600: #689F38;
--color-secondary-700: #558B2F;
--color-secondary-800: #33691E;
--color-secondary-900: #1B5E20;
```

### Accent Colors

```css
/* Accent - Warm Orange */
--color-accent-50: #FFF3E0;
--color-accent-100: #FFE0B2;
--color-accent-200: #FFCC80;
--color-accent-300: #FFB74D;
--color-accent-400: #FFA726;
--color-accent-500: #FF9800;  /* Main accent */
--color-accent-600: #FB8C00;
--color-accent-700: #F57C00;
--color-accent-800: #EF6C00;
--color-accent-900: #E65100;
```

### Neutral Colors

```css
/* Neutrals - Soft Grays */
--color-neutral-50: #FAFAFA;
--color-neutral-100: #F5F5F5;  /* Light background */
--color-neutral-200: #EEEEEE;
--color-neutral-300: #E0E0E0;
--color-neutral-400: #BDBDBD;
--color-neutral-500: #9E9E9E;
--color-neutral-600: #757575;
--color-neutral-700: #616161;
--color-neutral-800: #424242;
--color-neutral-900: #333333;  /* Dark text */
```

### Semantic Colors

```css
/* Success */
--color-success: #4CAF50;
--color-success-light: #81C784;
--color-success-dark: #388E3C;

/* Warning */
--color-warning: #FFC107;
--color-warning-light: #FFD54F;
--color-warning-dark: #FFA000;

/* Error */
--color-error: #F44336;
--color-error-light: #E57373;
--color-error-dark: #D32F2F;

/* Info */
--color-info: #2196F3;
--color-info-light: #64B5F6;
--color-info-dark: #1976D2;
```

### Usage Guidelines

- **Primary:** Main actions, headers, key UI elements
- **Secondary:** Supporting actions, secondary buttons, nature-related elements
- **Accent:** Highlights, hover states, calls-to-action
- **Neutral:** Text, backgrounds, borders, disabled states
- **Semantic:** Feedback states (success, error, warning, info)

---

## Typography

### Font Families

```css
/* Headings - Clean Sans-Serif */
--font-family-heading: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI',
                       'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;

/* Body - Readable Sans-Serif */
--font-family-body: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI',
                    'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;

/* Monospace - Code/Technical */
--font-family-mono: 'Fira Code', 'Courier New', Courier, monospace;
```

### Font Sizes (Responsive)

```css
/* Base: 16px */
--font-size-xs: 0.75rem;    /* 12px */
--font-size-sm: 0.875rem;   /* 14px */
--font-size-base: 1rem;     /* 16px */
--font-size-lg: 1.125rem;   /* 18px */
--font-size-xl: 1.25rem;    /* 20px */
--font-size-2xl: 1.5rem;    /* 24px */
--font-size-3xl: 1.875rem;  /* 30px */
--font-size-4xl: 2.25rem;   /* 36px */
--font-size-5xl: 3rem;      /* 48px */
--font-size-6xl: 3.75rem;   /* 60px */
```

### Font Weights

```css
--font-weight-light: 300;
--font-weight-normal: 400;
--font-weight-medium: 500;
--font-weight-semibold: 600;
--font-weight-bold: 700;
--font-weight-extrabold: 800;
```

### Line Heights

```css
--line-height-tight: 1.25;
--line-height-snug: 1.375;
--line-height-normal: 1.5;
--line-height-relaxed: 1.625;
--line-height-loose: 2;
```

### Typography Scale

```css
/* H1 - Page Title */
--h1-size: var(--font-size-4xl);
--h1-weight: var(--font-weight-bold);
--h1-line-height: var(--line-height-tight);
--h1-letter-spacing: -0.02em;

/* H2 - Section Title */
--h2-size: var(--font-size-3xl);
--h2-weight: var(--font-weight-bold);
--h2-line-height: var(--line-height-tight);
--h2-letter-spacing: -0.01em;

/* H3 - Subsection */
--h3-size: var(--font-size-2xl);
--h3-weight: var(--font-weight-semibold);
--h3-line-height: var(--line-height-snug);

/* H4 - Component Title */
--h4-size: var(--font-size-xl);
--h4-weight: var(--font-weight-semibold);
--h4-line-height: var(--line-height-snug);

/* H5 - Small Heading */
--h5-size: var(--font-size-lg);
--h5-weight: var(--font-weight-medium);
--h5-line-height: var(--line-height-normal);

/* H6 - Tiny Heading */
--h6-size: var(--font-size-base);
--h6-weight: var(--font-weight-medium);
--h6-line-height: var(--line-height-normal);

/* Body Text */
--body-size: var(--font-size-base);
--body-weight: var(--font-weight-normal);
--body-line-height: var(--line-height-relaxed);

/* Small Text */
--small-size: var(--font-size-sm);
--small-weight: var(--font-weight-normal);
--small-line-height: var(--line-height-normal);

/* Caption */
--caption-size: var(--font-size-xs);
--caption-weight: var(--font-weight-normal);
--caption-line-height: var(--line-height-normal);
```

### Accessibility Requirements

- **Minimum font size:** 16px for body text
- **Minimum contrast ratio:** 4.5:1 for normal text, 3:1 for large text (WCAG AA)
- **Line length:** Maximum 75 characters for optimal readability

---

## Spacing

### Spacing Scale

```css
--space-0: 0;
--space-1: 0.25rem;   /* 4px */
--space-2: 0.5rem;    /* 8px */
--space-3: 0.75rem;   /* 12px */
--space-4: 1rem;      /* 16px */
--space-5: 1.25rem;   /* 20px */
--space-6: 1.5rem;    /* 24px */
--space-8: 2rem;      /* 32px */
--space-10: 2.5rem;   /* 40px */
--space-12: 3rem;     /* 48px */
--space-16: 4rem;     /* 64px */
--space-20: 5rem;     /* 80px */
--space-24: 6rem;     /* 96px */
--space-32: 8rem;     /* 128px */
```

### Layout Spacing

```css
/* Container Padding */
--container-padding-mobile: var(--space-4);   /* 16px */
--container-padding-tablet: var(--space-6);   /* 24px */
--container-padding-desktop: var(--space-8);  /* 32px */

/* Section Spacing */
--section-spacing-mobile: var(--space-12);    /* 48px */
--section-spacing-tablet: var(--space-16);    /* 64px */
--section-spacing-desktop: var(--space-24);   /* 96px */

/* Component Spacing */
--component-spacing: var(--space-6);          /* 24px */
--component-spacing-sm: var(--space-4);       /* 16px */
--component-spacing-lg: var(--space-8);       /* 32px */
```

---

## Breakpoints

### Responsive Breakpoints

```css
/* Mobile First Approach */
--breakpoint-sm: 640px;   /* Small devices (landscape phones) */
--breakpoint-md: 768px;   /* Medium devices (tablets) */
--breakpoint-lg: 1024px;  /* Large devices (desktops) */
--breakpoint-xl: 1280px;  /* Extra large devices (large desktops) */
--breakpoint-2xl: 1536px; /* 2X large devices (extra large desktops) */
```

### Viewport Ranges

- **Mobile:** 320px - 639px (default styles)
- **Tablet:** 640px - 1023px
- **Desktop:** 1024px - 1535px
- **Large Desktop:** 1536px+

---

## Borders & Radius

### Border Widths

```css
--border-width-0: 0;
--border-width-1: 1px;
--border-width-2: 2px;
--border-width-4: 4px;
--border-width-8: 8px;
```

### Border Radius

```css
--radius-none: 0;
--radius-sm: 0.125rem;   /* 2px */
--radius-base: 0.25rem;  /* 4px */
--radius-md: 0.375rem;   /* 6px */
--radius-lg: 0.5rem;     /* 8px */
--radius-xl: 0.75rem;    /* 12px */
--radius-2xl: 1rem;      /* 16px */
--radius-3xl: 1.5rem;    /* 24px */
--radius-full: 9999px;   /* Pill shape */
```

### Border Colors

```css
--border-color-light: var(--color-neutral-200);
--border-color-default: var(--color-neutral-300);
--border-color-dark: var(--color-neutral-400);
--border-color-primary: var(--color-primary-500);
```

---

## Shadows

### Shadow Definitions

```css
/* Elevation Shadows */
--shadow-xs: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
--shadow-sm: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
--shadow-base: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
--shadow-md: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
--shadow-lg: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
--shadow-xl: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
--shadow-2xl: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
--shadow-inner: inset 0 2px 4px 0 rgba(0, 0, 0, 0.06);

/* Colored Shadows */
--shadow-primary: 0 4px 14px 0 rgba(74, 144, 226, 0.25);
--shadow-secondary: 0 4px 14px 0 rgba(124, 179, 66, 0.25);
```

### Usage Guidelines

- **xs, sm:** Subtle elevation (cards at rest)
- **base, md:** Standard elevation (buttons, cards on hover)
- **lg, xl:** Significant elevation (modals, dropdowns)
- **2xl:** Maximum elevation (important overlays)

---

## Transitions & Animations

### Timing Functions

```css
--ease-linear: cubic-bezier(0, 0, 1, 1);
--ease-in: cubic-bezier(0.4, 0, 1, 1);
--ease-out: cubic-bezier(0, 0, 0.2, 1);
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
--ease-yoga: cubic-bezier(0.4, 0.0, 0.2, 1);  /* Custom smooth easing */
```

### Duration

```css
--duration-fast: 150ms;
--duration-base: 200ms;
--duration-slow: 300ms;
--duration-slower: 500ms;
```

### Common Transitions

```css
/* Default transition for interactive elements */
--transition-default: all var(--duration-base) var(--ease-in-out);

/* Color transitions */
--transition-colors: background-color var(--duration-base) var(--ease-in-out),
                     border-color var(--duration-base) var(--ease-in-out),
                     color var(--duration-base) var(--ease-in-out);

/* Transform transitions */
--transition-transform: transform var(--duration-base) var(--ease-yoga);

/* Shadow transitions */
--transition-shadow: box-shadow var(--duration-base) var(--ease-in-out);
```

---

## Z-Index Scale

### Layering System

```css
--z-base: 0;
--z-dropdown: 1000;
--z-sticky: 1020;
--z-fixed: 1030;
--z-modal-backdrop: 1040;
--z-modal: 1050;
--z-popover: 1060;
--z-tooltip: 1070;
--z-notification: 1080;
```

---

## Iconography

### Icon System

- **Library:** Lucide React (https://lucide.dev/)
- **Size Scale:**
  - xs: 12px
  - sm: 16px
  - base: 20px
  - lg: 24px
  - xl: 32px
  - 2xl: 48px
- **Stroke Width:** 2px (consistent across all icons)
- **Style:** Line-based, minimal, clean

### Common Icons

- Navigation: Menu, X, ChevronRight, ChevronLeft, ArrowLeft
- Actions: Play, Pause, SkipForward, Heart, Share, Download
- Status: CheckCircle, AlertCircle, Info, XCircle
- User: User, UserCircle, Settings
- Content: Search, Filter, Grid, List, Calendar

---

## Component Guidelines

### Component Anatomy

Each component should follow this structure:
1. **Container:** Defines spacing and layout
2. **Content:** Main content area
3. **Actions:** Interactive elements (buttons, links)
4. **Feedback:** Loading states, errors, success messages

### State Variations

All interactive components should support:
- **Default:** Resting state
- **Hover:** Mouse over (desktop only)
- **Focus:** Keyboard navigation
- **Active:** Click/press state
- **Disabled:** Non-interactive state
- **Loading:** Processing state
- **Error:** Invalid state
- **Success:** Valid/complete state

### Accessibility Requirements

- **Keyboard Navigation:** All interactive elements must be keyboard accessible
- **Focus Indicators:** Visible focus states (outline or ring)
- **ARIA Labels:** Proper ARIA attributes for screen readers
- **Color Contrast:** Minimum 4.5:1 for normal text, 3:1 for large text
- **Touch Targets:** Minimum 44x44px for mobile
- **Alt Text:** Descriptive text for all images

---

## Usage Examples

### CSS Variables in Practice

```css
/* Button Primary */
.btn-primary {
  background-color: var(--color-primary-500);
  color: white;
  padding: var(--space-3) var(--space-6);
  border-radius: var(--radius-lg);
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  box-shadow: var(--shadow-sm);
  transition: var(--transition-colors), var(--transition-shadow);
}

.btn-primary:hover {
  background-color: var(--color-primary-600);
  box-shadow: var(--shadow-md);
}

/* Card */
.card {
  background-color: white;
  border-radius: var(--radius-xl);
  padding: var(--space-6);
  box-shadow: var(--shadow-base);
  transition: var(--transition-shadow);
}

.card:hover {
  box-shadow: var(--shadow-lg);
}
```

---

## Design Tokens (JSON)

For programmatic access, design tokens will be available as:

```json
{
  "colors": {
    "primary": "#4A90E2",
    "secondary": "#7CB342",
    "accent": "#FF9800"
  },
  "spacing": {
    "4": "1rem",
    "6": "1.5rem",
    "8": "2rem"
  },
  "typography": {
    "fontFamily": {
      "heading": "Inter, sans-serif",
      "body": "Inter, sans-serif"
    },
    "fontSize": {
      "base": "1rem",
      "lg": "1.125rem"
    }
  }
}
```

---

## Implementation Notes

### Tailwind CSS Configuration

This design system is optimized for Tailwind CSS. A Tailwind config will be generated with these tokens.

### CSS Custom Properties

All tokens are available as CSS custom properties (CSS variables) for maximum flexibility.

### Theme Support

Foundation for dark mode theming is included but implementation deferred to Phase 2.

---

## Version History

| Version | Date       | Changes                          |
|---------|------------|----------------------------------|
| 1.0     | 2025-12-05 | Initial design system created    |

---

**Questions or Feedback:** Contact UX Designer or @frontend-agent
