Here is the comprehensive **Product Requirement Document (PRD)** for the **SpeakVlog** application. This version removes all technical code (SQL/API) and focuses entirely on product logic, user experience, and detailed functional behavior.

---

# **Product Requirement Document (PRD): SpeakVlog**

**Version:** 2.0

**Status:** Draft

**Platform:** Mobile (iOS/Android) & Web

## **1\. Executive Summary**

**SpeakVlog** is an immersive English learning platform designed for intermediate-to-advanced learners. Unlike traditional apps that use textbook audio, SpeakVlog utilizes authentic, high-quality YouTube vlogs to teach real-world conversational English.

The core value proposition is **"Intensive Reading of Video" (视频精读)**. The app transforms passive video watching into an active learning experience through sentence-level looping, dual-subtitle controls, and interactive shadowing exercises. Access is strictly controlled via a paid **Activation Code** system to ensure a high-quality, exclusive community.

---

## **2\. User Personas**

* **The "Plateau" Learner (Primary):** Has studied English for years (CET-4/6 level) but cannot understand native speakers or Netflix shows without subtitles. Wants to learn "real" slang and natural intonation.  
* **The Global Professional:** Needs to improve listening and speaking for work. Time-poor, needs efficient, bite-sized learning (2-3 minute videos).

---

## **3\. Detailed Functional Requirements**

### **Module 1: Authentication & Account Security**

*Goal: Secure the platform, enforce the paid business model, and prevent account sharing.*

#### **1.1 Activation (Registration)**

* **Logic:** The app is "Invite-Only." Users cannot register without a valid, pre-purchased code.  
* **User Flow:**  
  1. User opens app → Selects "Register."  
  2. **Step 1:** Input Activation Code.  
  3. **Validation:** System checks if the code is valid and *unused*.  
     * *Error State:* "Invalid Code" or "Code already used."  
  4. **Step 2:** If valid, user sets up Mobile Number and Password.  
  5. **Completion:** Account is created, and the code is marked as "Burned" (Used).

#### **1.2 Secure Login**

* **Input:** 11-Digit Mobile Number \+ Password.  
* **Requirements:**  
  * Session Persistence: Users remain logged in until they explicitly log out or hit the device limit.  
  * Input Validation: Phone number format check (must be 11 digits).

#### **1.3 Device Concurrency Control (The "3-Device Limit")**

* **Logic:** A single account can strictly operate on a maximum of **3 devices** simultaneously.  
* **Behavior (Hard Block):**  
  * When User attempts to log in on **Device \#4**, the system **BLOCKS** the login.  
  * **Error Display:** A modal appears listing the currently active devices (e.g., *"Phone (Android), PC (Mac), Tablet (iPad)"*).  
  * **User Action Required:** The user must physically go to one of the old devices and log out. (Note: This is a strict security measure to prevent shared accounts).

---

### **Module 2: The "Intensive Reading" Video Player**

*Goal: Provide the ultimate tool for dissecting and mimicking native speech.*

#### **2.1 Smart Playback Controls**

* **Speed Control:** 0.5x, 0.75x, 1.0x (Pitch-corrected audio).  
* **Gesture Controls:**  
  * Double-tap right: Skip 5 seconds.  
  * Double-tap left: Rewind 5 seconds.  
  * Single tap: Pause/Play.  
* **Loop Modes:**  
  * **Single Sentence Loop (Critical):** Repeats the *current* subtitle line infinitely. Audio must loop seamlessly with no gaps.  
  * **A-B Repeat:** User can manually set Start/End points (optional advanced feature).

#### **2.2 Interactive Subtitles (The "Subtitle Stream")**

* **Visuals:** Subtitles are displayed as a scrollable card list below the video (Portrait mode) or overlaid (Landscape mode).  
* **Dual Language Toggle:**  
  1. Show Both (English \+ Chinese).  
  2. Show English Only (Testing mode).  
  3. Show Chinese Only (Translation mode).  
* **Click-to-Query:** Tapping any English word in the subtitle immediately:  
  1. Pauses the video.  
  2. Highlights the word.  
  3. Shows a pop-up dictionary definition with pronunciation.  
  4. Offers an "Add to Vocabulary" (+) button.

---

### **Module 3: Active Practice & Output**

*Goal: Move the user from passive listening to active speaking.*

#### **3.1 Shadowing Mode (跟读)**

* **Trigger:** Accessed via a "Microphone" icon on any sentence card.  
* **Flow:**  
  1. **Listen:** User plays the original audio for that specific sentence.  
  2. **Record:** User holds a button to record their own voice.  
  3. **Compare:** User plays their recording back-to-back with the original audio to self-correct intonation.  
  4. **Grading (Future):** AI scoring (0-100) based on pronunciation accuracy.

#### **3.2 Fill-in-the-Blanks (Cloze Test)**

* **Logic:** The system hides key vocabulary words in the subtitle.  
* **Action:** The user must listen to the audio and type (or select) the missing word.  
* **Feedback:** Instant Green (Correct) or Red (Incorrect) visual feedback.

---

### **Module 4: Content Discovery (The Feed)**

*Goal: Help users find the right content for their level/interest.*

#### **4.1 Video Feed Card**

Each video card in the list must display:

* Thumbnail (GIF or Static Image).  
* Title (Bilingual preferred).  
* **Difficulty Label:** (e.g., "Intermediate", "Advanced" \- color-coded).  
* **Duration:** (e.g., "2 min").  
* **Completion Status:** A checkmark if the user has watched it.

#### **4.2 Filtering & Sorting**

* **By Difficulty:** Level 1 (Easy) to Level 5 (Native Speed).  
* **By Accent:** American vs. British vs. Australian.  
* **By Topic:** Travel, Business, Food, Daily Life, Tech.

---

### **Module 5: User Profile & Progress Tracking**

*Goal: Gamify the experience to increase retention.*

#### **5.1 Learning Statistics**

* **Dashboard:** Displays "Total Sentences Learned," "Total Videos Completed," and "Study Duration (Minutes)."  
* **Streak System:** A calendar heat map (Github style) showing daily activity. If a user misses a day, the streak resets.

#### **5.2 "My Collection" (Personal Knowledge Base)**

* **Vocabulary Book:** List of all words saved during video playback.  
* **Sentence Book:** List of all sentences "Starred" by the user.  
* **Review Mode:** Clicking a saved sentence should deep-link back to the exact timestamp in the original video so the user can recall the context.

---

## **4\. Non-Functional Requirements (UX & Performance)**

### **4.1 Performance**

* **Video Buffering:** Must be instantaneous. Learners will jump back/forth frequently; latency \>1s is unacceptable.  
* **Subtitle Sync:** Subtitles must be synced to the millisecond. If the audio says "Hello" but the subtitle is 0.5s late, the "Sentence Loop" feature will fail.

### **4.2 Error Handling**

* **Network Loss:** If the user goes offline, the app should allow playback of *cached* videos (if download is supported) or show a friendly "Reconnecting..." toast.  
* **Login Conflicts:** As detailed in 1.3, the "Device Limit Reached" message must be explicit and helpful, not a generic "Login Failed" error.

### **4.3 Design Constraints**

* **Visual Style:** Minimalist, white/clean background, high contrast text for readability.  
* **Touch Targets:** Playback controls must be large enough to be tapped easily on a crowded subway (one-handed use).

---

## **5\. Security & Rate Limiting (Business Rules)**

* **Anti-Scraping:** The video API must have rate limits to prevent automated bots from stealing the premium content.  
* **Brute Force Protection:**  
  * **Login:** After 5 failed password attempts, lock the account for 15 minutes.  
  * **Activation Code:** After 3 invalid code entries, block the IP address for 1 hour to prevent guessing codes.

---

## **6.Security & API Rate Limiting Policy**

*Goal: Protect platform integrity, prevent "Brute Force" attacks, and stop content theft (scraping).*

#### **6.1 Rate Limiting Strategy**

The system must enforce limits at two levels:

1. **IP-Based (Pre-Login/Anonymous):** To prevent DDoS and mass account guessing.  
2. **UID-Based (Post-Login/Authenticated):** To prevent valid users from scraping content or abusing the API.

#### **6.2 Rate Limit Matrix (Business Rules)**

| Feature / API Module | Scope | Limit Rule (Threshold) | Triggered Action | Business Rationale |
| :---- | :---- | :---- | :---- | :---- |
| **Activation (Sign Up)** | **IP Address** | 5 requests / 10 mins | **Block IP (1 Hour)** | Prevents bots from randomly guessing 6-digit activation codes. |
| **Login (Auth)** | **IP Address** | 5 failed attempts / 1 min | **Temp Lock (15 min)** | Prevents "Credential Stuffing" (hackers testing stolen passwords). |
| **Login (Auth)** | **Target UID** | 5 failed attempts / 1 min | **Lock Account (Email Unlock)** | Protects a specific user account if they are being targeted. |
| **Video Playback** | **UID (User)** | 60 requests / 1 min | **Throttling (Slowdown)** | A human cannot load 60 videos in a minute. High traffic implies a scraper bot. |
| **Video Playback** | **IP Address** | 200 requests / 1 min | **Block IP (24 Hours)** | Prevents a single location (e.g., a data center) from scraping the library. |
| **SMS/Email Verification** | **IP Address** | 1 request / 60 sec | **Cool-down Timer** | Prevents SMS bombing (costing the company money). |
| **General API** | **UID (User)** | 1000 requests / 5 mins | **HTTP 429 Error** | General protection against buggy app versions or malicious scripts. |

#### **6.3 Violation Experience (UX)**

* **Soft Limit (Warning):** If a user clicks too fast (e.g., skips 10 videos in 5 seconds), show a "Toast" message: *"You're tapping too fast\! Please wait a moment."*  
* **Hard Limit (Block):**  
  * **Status Code:** Return HTTP 429 Too Many Requests.  
  * **User Message:** *"System has detected unusual traffic from your network. Please try again in \[X\] minutes."*  
* **Security Audit:** All rate-limit breaches must be logged in the "Admin Security Dashboard" for manual review.

---

### **Next Step**

This concludes the **Functional** and **Security** requirements. Would you like me to proceed to the **UI/UX Wireframe Descriptions** (explaining exactly what buttons go where on each screen) or the **Data Analytics Requirements** (what specific events to track for the marketing team)?

