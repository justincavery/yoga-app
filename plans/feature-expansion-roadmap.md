# Feature Expansion Roadmap

This roadmap implements the 4 major workstreams defined in `yoga-app-feature-expansion.md`:
- Workstream 2: Poses page auto-loading (infinite scroll)
- Workstream 3: Pose relationships (similar poses, progressions, sequences)
- Workstream 4: Sequence feature with timer
- Workstream 5: Pose instructions with text-to-speech

---

## Batch 1: Foundation (Parallel - All workstreams can start)

### Phase 1.1: Database Schema Updates
- **Status:** ⚪ Not Started
- **Agent:** TBD (backend specialist)
- **Effort:** M
- **Tasks:**
  - [ ] Create `pose_relationships` table with migration
  - [ ] Create `pose_sequences` junction table
  - [ ] Add instruction fields to poses table (entry_instructions, exit_instructions, holding_cues, breathing_pattern, has_side_variation)
  - [ ] Create indexes on foreign keys
  - [ ] Test migration on local database
- **Done When:** All migrations run successfully, tables exist with correct schema
- **Plan:** See `yoga-app-feature-expansion.md` - Data Model sections

### Phase 1.2: Backend API - Pose Pagination
- **Status:** ⚪ Not Started
- **Agent:** TBD (backend specialist)
- **Effort:** S
- **Tasks:**
  - [ ] Update `/api/v1/poses` endpoint to support `offset` and `limit` query params
  - [ ] Add default limit of 20 poses
  - [ ] Return total count in response headers
  - [ ] Update Pydantic models if needed
  - [ ] Add unit tests for pagination
- **Done When:** API endpoint returns paginated poses with correct offset/limit behavior
- **Plan:** `yoga-app-feature-expansion.md` - TR2.1

### Phase 1.3: Backend API - Pose Relationships
- **Status:** ⚪ Not Started
- **Agent:** TBD (backend specialist)
- **Effort:** M
- **Tasks:**
  - [ ] Create `/api/v1/poses/{id}/related` endpoint
  - [ ] Implement algorithm for finding similar poses (by category, difficulty)
  - [ ] Implement algorithm for progression poses (by difficulty level)
  - [ ] Return 2 similar and 2 progression poses
  - [ ] Add unit tests
- **Done When:** Endpoint returns relevant related poses for any pose ID
- **Plan:** `yoga-app-feature-expansion.md` - FR3.1 through FR3.6

### Phase 1.4: Backend API - Sequences CRUD
- **Status:** ⚪ Not Started
- **Agent:** TBD (backend specialist)
- **Effort:** M
- **Tasks:**
  - [ ] Create `/api/v1/sequences` endpoint (list, filter by category/difficulty)
  - [ ] Create `/api/v1/sequences/{id}` endpoint (get details with poses)
  - [ ] Create Pydantic models for sequences
  - [ ] Add unit tests
  - [ ] Document API in OpenAPI spec
- **Done When:** Can retrieve sequences list and individual sequence details via API
- **Plan:** `yoga-app-feature-expansion.md` - TR4.6

### Phase 1.5: Content Creation - Pose Instructions
- **Status:** ⚪ Not Started
- **Agent:** TBD (content creator / general purpose)
- **Effort:** L (split into sub-tasks)
- **Tasks:**
  - [ ] Write entry instructions for all 80 poses (3-5 steps each)
  - [ ] Write exit instructions for all 80 poses (2-3 steps each)
  - [ ] Add holding cues for each pose
  - [ ] Add breathing patterns for each pose
  - [ ] Identify poses with left/right variations (~15 poses)
  - [ ] Create SQL script to populate instruction fields
  - [ ] Run script on local database
- **Done When:** All 80 poses have complete instructions in database
- **Plan:** `yoga-app-feature-expansion.md` - TR5.3
- **Note:** This is large work - may need to be broken into batches of 20 poses

### Phase 1.6: Content Creation - 15 Sequences
- **Status:** ⚪ Not Started
- **Agent:** TBD (content creator / general purpose)
- **Effort:** M
- **Tasks:**
  - [ ] Create 15 sequence definitions (name, description, category, difficulty)
  - [ ] For each sequence, select 8-15 poses with durations
  - [ ] Assign position order for poses in sequences
  - [ ] Create SQL script to populate sequences and pose_sequences tables
  - [ ] Run script on local database
  - [ ] Verify sequences load via API
- **Done When:** 15 sequences exist in database with all poses linked
- **Plan:** `yoga-app-feature-expansion.md` - Appendix: Sequence Ideas

---

## Batch 2: Frontend Components (Depends on Batch 1 backend APIs)

### Phase 2.1: Infinite Scroll - Poses Page
- **Status:** 🔴 Blocked (needs Phase 1.2)
- **Agent:** TBD (frontend specialist)
- **Effort:** M
- **Tasks:**
  - [ ] Implement Intersection Observer for scroll detection
  - [ ] Update poses list component to fetch next batch
  - [ ] Add loading spinner component
  - [ ] Handle "no more poses" state
  - [ ] Add error handling for failed fetches
  - [ ] Test with all 80 poses
- **Done When:** User can scroll through all poses without pagination buttons, smooth loading
- **Depends On:** Phase 1.2
- **Plan:** `yoga-app-feature-expansion.md` - TR2.2, TR2.3

### Phase 2.2: Related Poses Component
- **Status:** 🔴 Blocked (needs Phase 1.3)
- **Agent:** TBD (frontend specialist)
- **Effort:** S
- **Tasks:**
  - [ ] Create RelatedPoses component
  - [ ] Fetch related poses from API
  - [ ] Display 2 similar poses with images and names
  - [ ] Display 2 progression poses with difficulty indicators
  - [ ] Make poses clickable (navigate to pose detail)
  - [ ] Add loading and error states
- **Done When:** Related poses section appears on pose detail pages with working navigation
- **Depends On:** Phase 1.3
- **Plan:** `yoga-app-feature-expansion.md` - FR3.1, FR3.2

### Phase 2.3: Sequence Links Component
- **Status:** 🔴 Blocked (needs Phase 1.4, 1.6)
- **Agent:** TBD (frontend specialist)
- **Effort:** S
- **Tasks:**
  - [ ] Create SequenceLinks component
  - [ ] Fetch sequences that include current pose
  - [ ] Display 3 sequences with names and difficulty
  - [ ] Make sequences clickable (navigate to sequence detail)
  - [ ] Add loading and error states
- **Done When:** Sequence links appear on pose detail pages, navigate to sequences
- **Depends On:** Phase 1.4, Phase 1.6
- **Plan:** `yoga-app-feature-expansion.md` - FR3.3, FR3.4

### Phase 2.4: Sequences Browser Page
- **Status:** 🔴 Blocked (needs Phase 1.4, 1.6)
- **Agent:** TBD (frontend specialist)
- **Effort:** M
- **Tasks:**
  - [ ] Create sequences list page route
  - [ ] Create SequenceCard component
  - [ ] Add filtering by category and difficulty
  - [ ] Create sequence detail page
  - [ ] Display pose list with durations on detail page
  - [ ] Add "Start Sequence" button
  - [ ] Add responsive design for mobile
- **Done When:** Users can browse and view sequence details
- **Depends On:** Phase 1.4, Phase 1.6
- **Plan:** `yoga-app-feature-expansion.md` - Sprint 4.1

---

## Batch 3: Sequence Player & Instructions (Depends on Batch 2)

### Phase 3.1: Sequence Player Component
- **Status:** 🔴 Blocked (needs Phase 2.4)
- **Agent:** TBD (frontend specialist)
- **Effort:** M
- **Tasks:**
  - [ ] Create SequencePlayer component with full-screen mode
  - [ ] Implement countdown timer (accurate to ±0.5s)
  - [ ] Add Web Audio API beeps (10s, 5s, 0s)
  - [ ] Implement auto-advance to next pose
  - [ ] Add progress indicator (pose X of Y)
  - [ ] Add pause/resume functionality
  - [ ] Add skip pose button
  - [ ] Test timer accuracy over 30-minute sequence
- **Done When:** Sequence player works smoothly with accurate timing and audio cues
- **Depends On:** Phase 2.4
- **Plan:** `yoga-app-feature-expansion.md` - Sprint 4.2

### Phase 3.2: Sequence Completion Screen
- **Status:** 🔴 Blocked (needs Phase 3.1)
- **Agent:** TBD (frontend specialist)
- **Effort:** S
- **Tasks:**
  - [ ] Create completion screen component
  - [ ] Display statistics (total time, poses completed)
  - [ ] Add "Practice Again" button
  - [ ] Add "Browse Sequences" button
  - [ ] Track completion in session storage
- **Done When:** Completion screen shows after sequence finishes
- **Depends On:** Phase 3.1
- **Plan:** `yoga-app-feature-expansion.md` - FR4.11

### Phase 3.3: Text-to-Speech Integration
- **Status:** 🔴 Blocked (needs Phase 1.5, Phase 3.1)
- **Agent:** TBD (frontend specialist)
- **Effort:** M
- **Tasks:**
  - [ ] Integrate Web Speech API
  - [ ] Create audio controller component
  - [ ] Add voice selection (male/female if available)
  - [ ] Add toggle for audio guidance
  - [ ] Synchronize TTS with pose timers
  - [ ] Test audio timing and quality
  - [ ] Add fallback for browsers without speech API
- **Done When:** Audio guidance plays during sequences, synced with pose changes
- **Depends On:** Phase 1.5, Phase 3.1
- **Plan:** `yoga-app-feature-expansion.md` - Sprint 5.1, 5.2

### Phase 3.4: Pose Instructions Display
- **Status:** 🔴 Blocked (needs Phase 1.5)
- **Agent:** TBD (frontend specialist)
- **Effort:** S
- **Tasks:**
  - [ ] Add instructions section to pose detail page
  - [ ] Display entry instructions (numbered list)
  - [ ] Display exit instructions
  - [ ] Display holding cues and breathing patterns
  - [ ] Add styling for readability
  - [ ] Handle left/right variations
- **Done When:** All instruction fields visible on pose pages
- **Depends On:** Phase 1.5
- **Plan:** `yoga-app-feature-expansion.md` - FR5.7

---

## Batch 4: Session Tracking & Polish (Depends on Batch 3)

### Phase 4.1: Session Tracking Backend
- **Status:** 🔴 Blocked (needs Phase 3.1)
- **Agent:** TBD (backend specialist)
- **Effort:** M
- **Tasks:**
  - [ ] Create `sequence_sessions` table migration
  - [ ] Create `/api/v1/sessions` endpoints (create, update, complete)
  - [ ] Track session start, completion, poses completed
  - [ ] Add session history endpoint
  - [ ] Add unit tests
- **Done When:** Sessions are tracked in database via API
- **Depends On:** Phase 3.1
- **Plan:** `yoga-app-feature-expansion.md` - Data Model

### Phase 4.2: Session Tracking Frontend
- **Status:** 🔴 Blocked (needs Phase 4.1)
- **Agent:** TBD (frontend specialist)
- **Effort:** S
- **Tasks:**
  - [ ] Integrate session API calls in sequence player
  - [ ] Save session on start
  - [ ] Update session on pause/resume
  - [ ] Complete session on finish
  - [ ] Display session history on dashboard
- **Done When:** User sessions are tracked and visible in dashboard
- **Depends On:** Phase 4.1

### Phase 4.3: Performance Optimization
- **Status:** 🔴 Blocked (needs all previous phases)
- **Agent:** TBD (backend optimizer)
- **Effort:** M
- **Tasks:**
  - [ ] Add database indexes for performance (poses, sequences, sessions)
  - [ ] Implement lazy loading for pose images
  - [ ] Add caching headers for static assets
  - [ ] Test page load times (<2s p95)
  - [ ] Test scroll performance (<100ms lag)
  - [ ] Run load testing (simulate 100 concurrent users)
- **Done When:** All performance metrics meet acceptance criteria
- **Depends On:** All previous phases
- **Plan:** `yoga-app-feature-expansion.md` - Success Metrics

---

## Batch 5: Testing & Deployment (Final)

### Phase 5.1: Integration Testing
- **Status:** 🔴 Blocked (needs all features complete)
- **Agent:** TBD (general purpose / QA)
- **Effort:** M
- **Tasks:**
  - [ ] Write end-to-end tests for infinite scroll
  - [ ] Write tests for pose relationships navigation
  - [ ] Write tests for sequence player (timer, audio, navigation)
  - [ ] Test TTS functionality across browsers
  - [ ] Test mobile responsiveness
  - [ ] Cross-browser testing (Chrome, Firefox, Safari, Edge)
- **Done When:** All critical paths tested and passing
- **Depends On:** All Batch 4 phases

### Phase 5.2: Content Validation
- **Status:** 🔴 Blocked (needs Phase 1.5, 1.6)
- **Agent:** TBD (content validator)
- **Effort:** S
- **Tasks:**
  - [ ] Review all pose instructions for accuracy
  - [ ] Verify left/right variations are documented
  - [ ] Test all 15 sequences for flow and timing
  - [ ] Verify sequence categorization is correct
  - [ ] Check for typos and grammatical errors
- **Done When:** All content reviewed and approved
- **Depends On:** Phase 1.5, Phase 1.6

### Phase 5.3: Production Deployment
- **Status:** 🔴 Blocked (needs all testing complete)
- **Agent:** TBD (devops deployer)
- **Effort:** S
- **Tasks:**
  - [ ] Run database migrations on production
  - [ ] Deploy backend updates
  - [ ] Deploy frontend updates
  - [ ] Verify all features working in production
  - [ ] Monitor error logs for 24 hours
- **Done When:** All features live and stable in production
- **Depends On:** Phase 5.1, Phase 5.2

---

## Success Metrics (Track Post-Launch)

### User Engagement
- [ ] Time on poses page increases by 40%
- [ ] Pose detail page views increase by 60%
- [ ] Sequence completion rate >70%
- [ ] Average session duration increases by 50%

### Feature Adoption
- [ ] 80% of users try at least one sequence
- [ ] 60% of users complete a full sequence
- [ ] 40% of users enable audio guidance
- [ ] Related pose clicks: 3+ per session

### Technical Performance
- [ ] Poses page scroll performance: <100ms lag
- [ ] Sequence timer accuracy: ±0.5 seconds
- [ ] TTS latency: <2 seconds from trigger
- [ ] API response times: <200ms p95

---

## Critical Path

The critical path for delivering value:
1. **Phase 1.2** → Phase 2.1 → Infinite scroll (Quick win)
2. **Phase 1.4, 1.6** → Phase 2.4 → Phase 3.1 → Sequence player (Core feature)
3. **Phase 1.5** → Phase 3.3 → TTS (Enhancement)

Prioritize Phases 1.2, 1.4, and 1.6 to unblock frontend work.

---

## Suggested First Action

Start Batch 1 with 4 agents in parallel:
1. **Backend Agent 1:** Phases 1.1, 1.2, 1.3, 1.4 (database and APIs)
2. **Content Agent:** Phases 1.5, 1.6 (instructions and sequences)
3. Wait for API completion before spawning frontend agents for Batch 2

---

**Created:** 2025-12-16
**Last Updated:** 2025-12-16
**Owner:** Project Manager Agent
