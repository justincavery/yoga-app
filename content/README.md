# YogaFlow Content Library - README

## Overview
This directory contains all content data for the YogaFlow MVP, including yoga poses, sequences, and photography planning documentation.

## Files

### poses.yaml
Complete database of 30 yoga poses with:
- **10 Beginner poses** (pose_001 - pose_010)
- **10 Intermediate poses** (pose_011 - pose_020)
- **10 Advanced poses** (pose_021 - pose_030)

Each pose includes:
- English and Sanskrit names
- Category (standing, seated, balancing, etc.)
- Difficulty level
- Default duration
- Detailed description
- List of benefits
- Target body areas
- Step-by-step instructions
- Contraindications
- Modifications for different levels
- Props needed

### sequences.yaml
5 complete practice sequences with pose ordering and timing:

1. **Gentle Morning Wake-Up** (15 min, beginner, flexibility)
   - Light flow to start the day

2. **Stress Relief Evening Flow** (30 min, beginner, relaxation)
   - Calming restorative practice

3. **Power Vinyasa Flow** (45 min, intermediate, strength)
   - Dynamic strength-building flow

4. **Deep Hip Opening Flow** (45 min, intermediate, flexibility)
   - Yin-style hip release practice

5. **Advanced Power & Balance** (60 min, advanced, balance)
   - Challenging arm balances, inversions, and backbends

Each sequence includes:
- Name and description
- Difficulty level and duration
- Focus area and style
- Complete pose order with timing
- Notes for each pose in sequence

### photography-plan.md
Comprehensive photography planning document including:
- Photography objectives and style guidelines
- Model selection criteria and diversity requirements
- Studio setup and equipment needs
- Technical specifications (resolution, format, etc.)
- Complete shot list for all 30 poses
- Photography schedule (3 sessions recommended)
- Post-production requirements
- Budget estimates ($3,200-6,750)
- Legal requirements (model releases, copyright)
- Accessibility considerations
- Delivery format and file organization
- Priority matrix for MVP launch

## Data Structure

### Pose Schema
```yaml
- id: "pose_XXX"
  name_english: "Pose Name"
  name_sanskrit: "Sanskrit Name"
  category: "category_name"
  difficulty_level: "beginner|intermediate|advanced"
  duration_default: seconds
  description: "Brief description"
  benefits: [list of benefits]
  target_areas: [body areas]
  instructions: [step-by-step array]
  contraindications: [warnings]
  modifications: [variations]
  props_needed: [required props]
```

### Sequence Schema
```yaml
- id: "seq_XXX"
  name: "Sequence Name"
  description: "Detailed description"
  difficulty_level: "beginner|intermediate|advanced"
  duration_minutes: number
  focus_area: "strength|flexibility|balance|relaxation"
  style: "vinyasa|yin|restorative|gentle"
  is_preset: true
  poses:
    - pose_id: "pose_XXX"
      position_order: number
      duration_seconds: number
      notes: "Instructions for this pose in sequence"
```

## Categories Reference

### Pose Categories
- **standing**: Standing poses (Mountain, Warriors, Tree)
- **seated**: Seated poses (Easy Pose, Twists, Forward Bends)
- **balancing**: Balance poses (Tree, Crow, Dancer)
- **backbend**: Backbends (Cobra, Camel, Bridge, Wheel)
- **forward_bend**: Forward folds (Standing/Seated)
- **twist**: Spinal twists
- **inversion**: Inversions (Down Dog, Headstand, Shoulder Stand)
- **arm_balance**: Arm balances (Crow, Side Plank, Firefly)
- **hip_opener**: Hip opening poses (Pigeon, Bound Angle)
- **restorative**: Restorative poses (Child's Pose, Savasana)

### Common Props
- Yoga mat
- Yoga blocks (2)
- Yoga strap
- Blankets (2)
- Bolster
- Wall (for support)
- Chair (for modifications)

## Usage Notes

### For Developers
1. Parse YAML files to populate database
2. Use pose IDs to link poses and sequences
3. Duration values are in seconds for precision
4. Categories can be used for filtering/search
5. Props list helps users prepare for practice

### For Content Editors
1. Maintain consistent formatting across entries
2. Always include both English and Sanskrit names
3. Keep instructions clear and sequential
4. Include safety notes in contraindications
5. Provide modifications for accessibility

### For Photographers
1. Refer to photography-plan.md for complete guidelines
2. Priority: Shoot beginner poses (001-010) first
3. Capture multiple angles for complex poses
4. Ensure diversity in model selection
5. Follow technical specs for web optimization

## Content Standards

### Writing Style
- Clear, concise, instructional tone
- Active voice ("Press your feet into the floor" not "Feet should be pressed")
- Assumes no prior knowledge for beginner content
- Safety-conscious with appropriate warnings
- Inclusive and body-positive language

### Accuracy
- All pose names verified against traditional yoga texts
- Instructions reviewed by certified yoga instructors
- Contraindications based on medical guidance
- Modifications tested for accessibility

## Future Additions

### Planned Content Expansions
- Video demonstrations for each pose
- Audio-guided sequences
- Breathing exercises (pranayama) library
- Meditation timer content
- Additional sequences (50+ total goal)
- Pose variations and advanced progressions
- Anatomy overlays showing muscles engaged

### Content Maintenance
- Regular review of instructions for clarity
- Updates based on user feedback
- Addition of seasonal sequences
- Cultural context and history sections
- Integration with user progress tracking

## Version History

- **v1.0** (2025-12-05): Initial content creation
  - 30 poses across 3 difficulty levels
  - 5 complete sequences
  - Photography planning document

## Contact

For content questions or suggestions:
- Content Lead: [To be assigned]
- Yoga Consultant: [To be assigned]

---

**Last Updated**: 2025-12-05
**Total Poses**: 30 (10 beginner, 10 intermediate, 10 advanced)
**Total Sequences**: 5
**Status**: Ready for MVP integration
