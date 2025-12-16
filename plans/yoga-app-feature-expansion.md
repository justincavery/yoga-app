# Yoga App Feature Expansion - Project Plan

## Executive Summary
This document outlines the requirements, roadmap, and project plan for expanding the YogaFlow application with four major workstreams: poses page enhancement, pose relationships, sequence functionality, and pose instructions with text-to-speech.

---

## Workstream 2: Poses Page Auto-loading

### Requirements

#### Functional Requirements
- FR2.1: Implement infinite scroll on /poses page to load more poses as user scrolls
- FR2.2: Load poses in batches of 20 at a time
- FR2.3: Show loading indicator while fetching next batch
- FR2.4: Handle end of list gracefully (no more poses message)
- FR2.5: Maintain current filtering and sorting capabilities

#### Technical Requirements
- TR2.1: Update `/api/v1/poses` endpoint to support `offset` and `limit` parameters
- TR2.2: Implement frontend intersection observer for scroll detection
- TR2.3: Add loading state management in React
- TR2.4: Optimize query performance with database indexes

#### User Stories
- **US2.1**: As a user, I want to see more poses as I scroll down so I don't have to navigate through pages
- **US2.2**: As a user, I want a smooth loading experience so the app feels responsive

#### Acceptance Criteria
- User can scroll through all 80 poses without pagination
- New poses load automatically when scrolling near bottom (300px threshold)
- Loading indicator appears during fetch
- No duplicate poses appear
- Performance remains smooth (<100ms scroll lag)

---

## Workstream 3: Pose Relationships & Sequences

### Requirements

#### Functional Requirements
- FR3.1: Display 2 similar poses on each pose detail page
- FR3.2: Display 2 progression poses (next level difficulty or related)
- FR3.3: Display 3 sequences that include the current pose
- FR3.4: Make all recommendations clickable to navigate
- FR3.5: Similar poses based on category and difficulty
- FR3.6: Progression poses based on difficulty level and muscle groups

#### Technical Requirements
- TR3.1: Create `pose_relationships` table with relationship types
- TR3.2: Add API endpoint `/api/v1/poses/{id}/related`
- TR3.3: Implement recommendation algorithm for similar poses
- TR3.4: Create `pose_sequences` junction table
- TR3.5: Update pose detail endpoint to include relationships

#### Data Model Changes
```sql
-- Pose Relationships
CREATE TABLE pose_relationships (
    id SERIAL PRIMARY KEY,
    pose_id INTEGER REFERENCES poses(pose_id),
    related_pose_id INTEGER REFERENCES poses(pose_id),
    relationship_type VARCHAR(50), -- 'similar', 'progression'
    created_at TIMESTAMP DEFAULT NOW()
);

-- Pose-Sequence Junction
CREATE TABLE pose_sequences (
    id SERIAL PRIMARY KEY,
    pose_id INTEGER REFERENCES poses(pose_id),
    sequence_id INTEGER REFERENCES sequences(sequence_id),
    position INTEGER, -- order in sequence
    duration_seconds INTEGER DEFAULT 30
);
```

#### User Stories
- **US3.1**: As a user, I want to see similar poses so I can explore alternatives
- **US3.2**: As a user, I want to see progression poses so I know what to practice next
- **US3.3**: As a user, I want to see which sequences include this pose so I can practice them

#### Acceptance Criteria
- 2 similar poses displayed with images and names
- 2 progression poses displayed with difficulty indicators
- 3 sequences listed with names and difficulty levels
- All items are clickable and navigate correctly
- Recommendations are relevant and accurate

---

## Workstream 4: Sequence Feature

### Requirements

#### Functional Requirements
- FR4.1: Create 15 curated sequences covering different goals and difficulties
- FR4.2: Sequence categories: Relaxation, Easy Morning, Back Focus, Leg Focus, Restorative, Invigorating, Core Strength
- FR4.3: Each category has Easy/Medium/Hard variations
- FR4.4: Users can "Start Sequence" to begin guided practice
- FR4.5: Display current pose with image and name
- FR4.6: Show timer counting down for each pose
- FR4.7: Audio beeps at 10 seconds, 5 seconds, and 0 seconds
- FR4.8: Auto-advance to next pose when timer completes
- FR4.9: Display progress (pose X of Y)
- FR4.10: Allow pause/resume and skip pose functionality
- FR4.11: Show completion screen with statistics

#### Additional Use Cases for Timer/Sequence Feature
1. **HIIT/Circuit Training**: Timer for workout intervals
2. **Meditation Sessions**: Timed meditation segments
3. **Breathwork Practices**: Timed breathing cycles
4. **Stretching Routines**: Pre/post-workout stretches
5. **Physical Therapy**: Guided exercise routines
6. **Dance/Movement Classes**: Choreography practice
7. **Cooking/Recipes**: Step-by-step timed instructions
8. **Study Sessions**: Pomodoro technique implementation
9. **Kids Activities**: Timed activity rotations
10. **Team Building Exercises**: Group activity rotations

#### Technical Requirements
- TR4.1: Create `sequences` table with metadata
- TR4.2: Populate with 15 curated sequences
- TR4.3: Implement sequence player component with timer
- TR4.4: Add Web Audio API for beep sounds
- TR4.5: Create session tracking for completed sequences
- TR4.6: API endpoints for sequences and session tracking

#### Data Model
```sql
-- Sequences
CREATE TABLE sequences (
    sequence_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    category VARCHAR(50), -- 'relaxation', 'back_focus', etc.
    difficulty_level VARCHAR(20), -- 'easy', 'medium', 'hard'
    total_duration INTEGER, -- seconds
    image_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Sequence Sessions (tracking)
CREATE TABLE sequence_sessions (
    session_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    sequence_id INTEGER REFERENCES sequences(sequence_id),
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    poses_completed INTEGER,
    total_poses INTEGER
);
```

#### User Stories
- **US4.1**: As a user, I want to browse sequences by category and difficulty
- **US4.2**: As a user, I want to start a guided sequence with timers
- **US4.3**: As a user, I want audio cues so I know when to transition
- **US4.4**: As a user, I want to pause/resume my practice
- **US4.5**: As a user, I want to see my completion statistics

#### Acceptance Criteria
- 15 sequences created and categorized correctly
- Sequence player shows current pose with clear visuals
- Timer counts down accurately
- Beeps play at correct intervals (10s, 5s, 0s)
- Auto-advance works smoothly
- Pause/resume maintains state
- Completion screen shows summary

---

## Workstream 5: Pose Instructions & Text-to-Speech

### Requirements

#### Functional Requirements
- FR5.1: Create detailed entry instructions for each pose (3-5 steps)
- FR5.2: Create detailed exit instructions for each pose (2-3 steps)
- FR5.3: Include holding cues and breathing instructions
- FR5.4: Create left/right variations where applicable (e.g., Warrior II, Triangle)
- FR5.5: Integrate text-to-speech during sequences
- FR5.6: Allow users to toggle audio guidance on/off
- FR5.7: Display instructions as text on pose detail pages
- FR5.8: Support multiple voice options (male/female)

#### Technical Requirements
- TR5.1: Add instruction fields to poses table
- TR5.2: Integrate Web Speech API or external TTS service
- TR5.3: Create instruction content for all 80 poses
- TR5.4: Implement audio playback controller
- TR5.5: Add user preferences for voice settings

#### Data Model Changes
```sql
ALTER TABLE poses ADD COLUMN entry_instructions TEXT[];
ALTER TABLE poses ADD COLUMN exit_instructions TEXT[];
ALTER TABLE poses ADD COLUMN holding_cues TEXT;
ALTER TABLE poses ADD COLUMN breathing_pattern TEXT;
ALTER TABLE poses ADD COLUMN has_side_variation BOOLEAN DEFAULT FALSE;
```

#### User Stories
- **US5.1**: As a user, I want step-by-step instructions so I can learn poses correctly
- **US5.2**: As a user, I want audio guidance during sequences so I don't have to look at the screen
- **US5.3**: As a user, I want clear exit instructions so I can transition safely
- **US5.4**: As a user, I want breathing cues integrated into instructions

#### Acceptance Criteria
- All 80 poses have entry/exit instructions
- Instructions are clear and concise (2-5 sentences each)
- Left/right variations documented for ~15 poses
- TTS audio is clear and natural-sounding
- Audio synchronizes with pose timers
- Users can toggle audio on/off
- Text instructions visible on pose pages

---

## Subject Matter Expert Recommendations

### Best Practices for Sequence Design
1. **Flow Principle**: Sequences should flow naturally (standing → floor → standing is jarring)
2. **Warm-up/Cool-down**: Always include gentle poses at start and end
3. **Duration Guidelines**:
   - Easy poses: 30-45 seconds
   - Medium poses: 45-60 seconds
   - Advanced poses: 60-90 seconds
4. **Balance**: Include forward bends, backbends, twists, and lateral bends
5. **Safety**: Never go straight into advanced poses without warm-up

### Recommended Sequence Structure (Example)
```
1. Opening (2-3 min): Centering, breathing
2. Warm-up (5-7 min): Gentle stretches
3. Main Practice (15-20 min): Focus poses
4. Cool-down (5 min): Gentle releases
5. Savasana (3-5 min): Final relaxation
```

### Text-to-Speech Script Guidelines
- Use second person ("You")
- Present tense for actions ("Place your foot...")
- Include breathing cues ("Inhale as you lift...")
- Add safety reminders ("Keep your core engaged...")
- Pace: ~120-140 words per minute
- Pause between instructions: 2-3 seconds

---

## Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)
**Goal**: Set up data structures and core functionality

**Sprint 1.1 - Database & API (Week 1)**
- Create new database tables (relationships, sequences, sessions)
- Add instruction fields to poses table
- Create API endpoints for sequences
- Implement pagination on poses endpoint
- **Deliverable**: Updated database schema and API endpoints

**Sprint 1.2 - Content Creation (Week 2)**
- Write instructions for all 80 poses
- Create 15 sequence definitions
- Define pose relationships (similar/progression)
- Populate database with content
- **Deliverable**: Complete content in database

### Phase 2: Poses Page Enhancement (Week 3)
**Goal**: Improve poses browsing experience

**Sprint 2.1 - Infinite Scroll**
- Implement frontend intersection observer
- Update poses list component
- Add loading states
- Test performance with all poses
- **Deliverable**: Working infinite scroll on /poses

### Phase 3: Pose Relationships (Week 4)
**Goal**: Add related poses and sequences to pose detail pages

**Sprint 3.1 - Related Poses UI**
- Create RelatedPoses component
- Fetch and display similar poses
- Fetch and display progression poses
- Add navigation links
- **Deliverable**: Related poses section on pose pages

**Sprint 3.2 - Sequence Links**
- Create SequenceLinks component
- Display sequences including current pose
- Add click-through to sequence detail
- **Deliverable**: Sequence links on pose pages

### Phase 4: Sequence Player (Weeks 5-6)
**Goal**: Build guided sequence functionality

**Sprint 4.1 - Sequence Browser (Week 5)**
- Create sequences list page
- Add filtering by category/difficulty
- Create sequence detail page
- Show pose list with durations
- **Deliverable**: Sequence browsing interface

**Sprint 4.2 - Sequence Player (Week 6)**
- Build timer component
- Implement audio beeps
- Add pose progression logic
- Create pause/resume functionality
- Add progress indicator
- Build completion screen
- **Deliverable**: Working sequence player

### Phase 5: Text-to-Speech Integration (Weeks 7-8)
**Goal**: Add audio guidance to sequences

**Sprint 5.1 - TTS Implementation (Week 7)**
- Integrate Web Speech API
- Create audio controller
- Test voice quality and timing
- Add voice selection options
- **Deliverable**: Basic TTS functionality

**Sprint 5.2 - Sequence Audio (Week 8)**
- Integrate TTS with sequence player
- Synchronize audio with timers
- Add toggle controls
- Test full sequence with audio
- **Deliverable**: Audio-guided sequences

### Phase 6: Polish & Testing (Week 9)
**Goal**: Refine and test all features

**Sprint 6.1 - Integration Testing**
- End-to-end testing of all workstreams
- User acceptance testing
- Performance optimization
- Bug fixes
- **Deliverable**: Production-ready features

---

## Project Timeline Summary

| Phase | Duration | Key Deliverables |
|-------|----------|------------------|
| Phase 1: Foundation | 2 weeks | Database schema, API endpoints, Content |
| Phase 2: Poses Page | 1 week | Infinite scroll |
| Phase 3: Relationships | 1 week | Related poses, Sequence links |
| Phase 4: Sequences | 2 weeks | Sequence browser, Player with timer |
| Phase 5: TTS | 2 weeks | Audio guidance |
| Phase 6: Polish | 1 week | Testing, optimization |
| **Total** | **9 weeks** | **Complete feature set** |

---

## Risk Assessment

### Technical Risks
1. **Risk**: TTS quality varies across browsers
   - **Mitigation**: Test on all major browsers, provide fallback text

2. **Risk**: Audio synchronization issues during sequences
   - **Mitigation**: Thorough timing testing, adjustable delays

3. **Risk**: Performance issues with 80 poses infinite scroll
   - **Mitigation**: Virtual scrolling, image lazy loading

### Content Risks
1. **Risk**: Inaccurate pose instructions could cause injury
   - **Mitigation**: SME review, legal disclaimer

2. **Risk**: Sequence flows may not be optimal
   - **Mitigation**: Yoga instructor review and iteration

3. **Risk**: TTS may mispronounce Sanskrit names
   - **Mitigation**: Phonetic spelling, pre-recorded audio for names

### Dependency Risks
1. **Risk**: Workstream 5 depends on Workstream 4 completion
   - **Mitigation**: Can develop TTS infrastructure in parallel

2. **Risk**: Missing pose images (6 poses)
   - **Mitigation**: Generate remaining images in Phase 1

---

## Success Metrics

### User Engagement
- Time spent on poses page increases by 40%
- Pose detail page views increase by 60%
- Sequence completion rate >70%
- Average session duration increases by 50%

### Feature Adoption
- 80% of users try at least one sequence
- 60% of users complete a full sequence
- 40% of users enable audio guidance
- Related pose clicks: 3+ per session

### Technical Performance
- Poses page scroll performance: <100ms lag
- Sequence timer accuracy: ±0.5 seconds
- TTS latency: <2 seconds from trigger
- API response times: <200ms p95

---

## Next Steps

### Immediate Actions (This Week)
1. ✅ Generate missing 6 pose images
2. ⏳ Review and approve this project plan
3. ⏳ Assign team roles and responsibilities
4. ⏳ Set up project tracking (GitHub Projects/Jira)

### Week 1 Kickoff
1. Database schema creation
2. API endpoint development
3. Begin content writing for pose instructions
4. Start sequence definitions

### Approval Required
- [ ] Project plan approved by stakeholder
- [ ] Timeline and resource allocation approved
- [ ] Content creation approach approved
- [ ] Technical architecture approved

---

## Appendix: Sequence Ideas (15 Sequences)

### Relaxation Category
1. **Gentle Evening Unwind** (Easy) - 15 min
2. **Deep Relaxation Flow** (Medium) - 25 min
3. **Restorative Stress Relief** (Easy) - 30 min

### Morning/Energizing
4. **Morning Wake-Up** (Easy) - 10 min
5. **Energizing Flow** (Medium) - 20 min
6. **Invigorating Power Sequence** (Hard) - 30 min

### Body-Specific Focus
7. **Gentle Back Care** (Easy) - 15 min
8. **Back Strengthening** (Medium) - 25 min
9. **Advanced Backbend Practice** (Hard) - 30 min
10. **Leg & Hip Opening** (Easy) - 20 min
11. **Strong Legs & Balance** (Medium) - 25 min

### Specialized
12. **Core Foundations** (Medium) - 20 min
13. **Flexibility Builder** (Medium) - 25 min
14. **Arm Balance Progression** (Hard) - 30 min
15. **Full Body Integration** (Hard) - 35 min

---

**Document Version**: 1.0
**Last Updated**: 2025-12-16
**Owner**: YogaFlow Product Team
**Review Date**: TBD
