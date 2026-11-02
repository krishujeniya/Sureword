/**
 * Sureword — Sovereign Frontline Voice Documentation Engine
 * Production Client Application Logic
 */

// Application State
let currentDraftId = null;
let currentVersion = 1;
let currentLanguage = "en"; // "en" | "hi"
let mediaRecorder = null;
let audioChunks = [];
let recordTimerInterval = null;
let recordStartTime = 0;
let isClarifyingField = null;
let committedRecordsCache = [];

// Bilingual Localization Dictionary
const I18N = {
  en: {
    tagline: "Frontline Healthcare Voice Documentation",
    tab_form_text: "Visit Entry",
    tab_registry_text: "Saved Registry",
    step1_title: "Dictate Visit",
    step1_desc: "Speak visit details in Hindi or English (Name, Age, Village, Visit Date).",
    presets_label: "Quick Test:",
    record_start: "Start Dictation",
    record_stop: "Stop Dictation",
    transcript_title: "Live Transcript",
    step2_title: "Structured Visit Form",
    btn_new_session_text: "New Visit",
    clarify_alert_title: "Clarification Needed",
    btn_hear_prompt: "Hear Prompt",
    btn_speak_field: "Speak Answer",
    btn_save_edit: "Save",
    label_name: "Patient Name",
    label_age: "Age (Years)",
    label_village: "Village",
    label_date: "Visit Date",
    commit_info_incomplete: "Fill all 4 fields to save record.",
    commit_info_ready: "All fields verified. Ready to save.",
    commit_info_committed: "Visit record saved.",
    btn_commit: "Save Visit Record",
    committed_heading: "Visit Record Saved",
    record_id_label: "Record ID:",
    registry_title: "Saved Visit Records",
    registry_subtitle: "Locally verified household visit documentation."
  },
  hi: {
    tagline: "सामुदायिक स्वास्थ्य वॉयस प्रलेखन",
    tab_form_text: "भेंट प्रपत्र",
    tab_registry_text: "सहेजे गए रिकॉर्ड",
    step1_title: "भेंट विवरण बोलें",
    step1_desc: "हिन्दी या अंग्रेजी में मरीज का विवरण बोलें (नाम, उम्र, गाँव, तारीख)।",
    presets_label: "त्वरित परीक्षण:",
    record_start: "बोलना शुरू करें",
    record_stop: "रिकॉर्डिंग रोकें",
    transcript_title: "वाक् प्रतिलेखन",
    step2_title: "संरचित चिकित्सा प्रपत्र",
    btn_new_session_text: "नई भेंट",
    clarify_alert_title: "स्पष्टीकरण आवश्यक",
    btn_hear_prompt: "प्रश्न सुनें",
    btn_speak_field: "उत्तर बोलें",
    btn_save_edit: "सहेजें",
    label_name: "मरीज का नाम",
    label_age: "आयु (वर्ष)",
    label_village: "गाँव",
    label_date: "भेंट की तारीख",
    commit_info_incomplete: "रिकॉर्ड सहेजने के लिए सभी 4 फ़ील्ड भरें।",
    commit_info_ready: "सभी फ़ील्ड सत्यापित हैं। सहेजने के लिए तैयार।",
    commit_info_committed: "रिकॉर्ड सहेजा गया।",
    btn_commit: "रिकॉर्ड सहेजें",
    committed_heading: "भेंट रिकॉर्ड सहेजा गया",
    record_id_label: "रिकॉर्ड आईडी:",
    registry_title: "सहेजे गए भेंट रिकॉर्ड",
    registry_subtitle: "सत्यापित घरेलू भेंटों की स्थानीय पंजी।"
  }
};

// Preset Dictations
const PRESET_SCRIPTS = {
  kamla: "मरीज का नाम कमला देवी है, उम्र 150 साल, गाँव रामपुर, विजिट डेट 30 अक्टूबर 2026",
  sunita: "पेशेंट नेम सुनीता बाई, एज अडतीस साल, गांव बिलासपुर, विजिट डेट आज",
  ramesh: "patient name Ramesh Kumar, age 52 years, village Sonpur, visit date 15 August 2026"
};

const FIELD_KEYS = ["person_name", "age", "village", "visit_date"];

// DOM References
const providerBadge = document.getElementById("provider-badge");
const langToggleBtn = document.getElementById("lang-toggle-btn");
const currentLangText = document.getElementById("current-lang-text");
const recordBtn = document.getElementById("record-btn");
const recordText = document.getElementById("record-text");
const recordingTimer = document.getElementById("recording-timer");
const audioWaveContainer = document.getElementById("audio-wave-container");
const statusMessage = document.getElementById("status-message");
const transcriptContent = document.getElementById("transcript-content");
const newDraftBtn = document.getElementById("new-draft-btn");
const clarificationBanner = document.getElementById("clarification-banner");
const clarifyFieldTitle = document.getElementById("clarify-field-title");
const clarifyPromptText = document.getElementById("clarify-prompt-text");
const playTtsBtn = document.getElementById("play-tts-btn");
const clarifyMicBtn = document.getElementById("clarify-mic-btn");
const clarifyManualInput = document.getElementById("clarify-manual-input");
const clarifySaveBtn = document.getElementById("clarify-save-btn");
const commitBtn = document.getElementById("commit-btn");
const commitValidationInfo = document.getElementById("commit-validation-info");
const committedResult = document.getElementById("committed-result");
const savedRecordId = document.getElementById("saved-record-id");
const savedJson = document.getElementById("saved-json");
const ttsAudioPlayer = document.getElementById("tts-audio-player");

// Navigation Tabs & Views
const tabFormBtn = document.getElementById("tab-form-btn");
const tabRegistryBtn = document.getElementById("tab-registry-btn");
const viewForm = document.getElementById("view-form");
const viewRegistry = document.getElementById("view-registry");
const registryCountPill = document.getElementById("registry-count-pill");
const registryTableBody = document.getElementById("registry-table-body");
const refreshRegistryBtn = document.getElementById("refresh-registry-btn");
const exportCsvBtn = document.getElementById("export-csv-btn");
const exportJsonBtn = document.getElementById("export-json-btn");
const exportCsvBtn = document.getElementById("export-csv-btn");
const exportJsonBtn = document.getElementById("export-json-btn");

// App Initialization
window.addEventListener("DOMContentLoaded", async () => {
  await checkHealth();
  await loadCommittedRecords();

  const urlParams = new URLSearchParams(window.location.search);
  const existingDraftId = urlParams.get("draft_id");
  if (existingDraftId) {
    await loadExistingDraft(existingDraftId);
  } else {
    await initNewDraft();
  }

  setupEventListeners();
  setupKeyboardShortcuts();
});

// Localization Engine
function setLanguage(lang) {
  currentLanguage = lang;
  currentLangText.textContent = lang === "en" ? "हिन्दी" : "English";

  const strings = I18N[lang] || I18N.en;
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const key = el.getAttribute("data-i18n");
    if (strings[key]) {
      el.textContent = strings[key];
    }
  });

  document.documentElement.lang = lang;
}

function toggleLanguage() {
  const nextLang = currentLanguage === "en" ? "hi" : "en";
  setLanguage(nextLang);
}

// System Health Check
async function checkHealth() {
  try {
    const res = await fetch("/healthz");
    const data = await res.json();
    if (data.gnani_configured) {
      providerBadge.textContent = "● Live Speech Online";
      providerBadge.className = "badge badge-live";
    } else {
      providerBadge.textContent = "● Speech Engine Ready";
      providerBadge.className = "badge badge-fixture";
    }
  } catch (err) {
    providerBadge.textContent = "○ Offline Mode";
    providerBadge.className = "badge badge-warning";
  }
}

// Draft Session Lifecycle
async function initNewDraft() {
  showStatus("Initializing frontline visit session...", "info");
  try {
    const res = await fetch("/api/drafts", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: `language=${encodeURIComponent(currentLanguage === "hi" ? "hi-IN" : "hi-IN")}`
    });
    const data = await res.json();
    currentDraftId = data.draft_id;
    currentVersion = data.version;
    updateStateUI(data.state, currentVersion);
    resetFormUI();
    hideStatus();
  } catch (err) {
    showStatus("Failed to initialize draft session: " + err.message, "error");
  }
}

async function loadExistingDraft(draftId) {
  showStatus(`Loading visit draft ${draftId}...`, "info");
  try {
    const res = await fetch(`/api/drafts/${draftId}`);
    if (res.ok) {
      const data = await res.json();
      currentDraftId = data.draft_id;
      currentVersion = data.version;
      renderDraft(data);
      hideStatus();
    } else {
      await initNewDraft();
    }
  } catch (err) {
    await initNewDraft();
  }
}

function resetFormUI() {
  committedResult.classList.add("hidden");
  clarificationBanner.classList.add("hidden");
  transcriptContent.textContent = "No audio transcribed yet. Click 'Start Dictation' or select a sample above.";

  FIELD_KEYS.forEach((key) => {
    const input = document.getElementById(`field-${key}`);
    const tag = document.getElementById(`tag-${key}`);
    const reasons = document.getElementById(`reasons-${key}`);
    if (input) input.value = "";
    if (tag) {
      tag.textContent = "Missing";
      tag.className = "status-tag tag-missing";
    }
    if (reasons) reasons.innerHTML = "";
  });

  commitBtn.disabled = true;
  commitValidationInfo.textContent = I18N[currentLanguage].commit_info_incomplete;
}

function updateStateUI(state, version) {
  if (stateBadge) {
    stateBadge.textContent = state;
    stateBadge.className = "badge " + (
      state === "READY_FOR_REVIEW" ? "badge-live" :
      state === "NEEDS_CLARIFICATION" ? "badge-fixture" :
      state === "COMMITTED" ? "badge-live" : "badge-neutral"
    );
  }
  if (versionBadge) {
    versionBadge.textContent = `v${version}`;
  }
}

function renderDraft(draft) {
  currentDraftId = draft.draft_id;
  currentVersion = draft.version;
  updateStateUI(draft.state, currentVersion);

  let allValid = true;

  FIELD_KEYS.forEach((key) => {
    const f = draft.fields[key];
    const input = document.getElementById(`field-${key}`);
    const tag = document.getElementById(`tag-${key}`);
    const reasonsDiv = document.getElementById(`reasons-${key}`);

    if (f) {
      if (input && f.canonical_value) {
        input.value = f.canonical_value;
      }
      if (tag) {
        tag.textContent = formatStatus(f.status);
        tag.className = `status-tag tag-${f.status}`;
      }
      if (reasonsDiv) {
        reasonsDiv.innerHTML = f.reasons.length ? f.reasons.join("<br>") : "";
      }

      if (f.status === "missing" || f.status === "needs_repeat" || !f.canonical_value) {
        allValid = false;
      }
    } else {
      allValid = false;
    }
  });

  // Handle Clarification Banner (Policy P)
  if (draft.state === "NEEDS_CLARIFICATION" && draft.active_prompt) {
    clarificationBanner.classList.remove("hidden");
    isClarifyingField = draft.active_prompt.target_field;
    clarifyFieldTitle.textContent = `${I18N[currentLanguage].clarify_alert_title}: ${formatFieldName(isClarifyingField)}`;
    clarifyPromptText.textContent = draft.active_prompt.prompt_text;
    clarifyManualInput.value = "";
    clarifyManualInput.focus();
  } else {
    clarificationBanner.classList.add("hidden");
    isClarifyingField = null;
  }

  // Handle Commit button & validation feedback
  if (draft.state === "READY_FOR_REVIEW" && allValid) {
    commitBtn.disabled = false;
    commitValidationInfo.textContent = I18N[currentLanguage].commit_info_ready;
  } else if (draft.state === "COMMITTED") {
    commitBtn.disabled = true;
    commitValidationInfo.textContent = I18N[currentLanguage].commit_info_committed;
  } else {
    commitBtn.disabled = true;
    commitValidationInfo.textContent = I18N[currentLanguage].commit_info_incomplete;
  }
}

function formatStatus(status) {
  switch (status) {
    case "missing": return "Missing";
    case "proposed": return "Proposed";
    case "needs_repeat": return "Needs Repeat";
    case "user_confirmed": return "Confirmed ✓";
    case "manually_edited": return "Edited ✎";
    default: return status;
  }
}

function formatFieldName(key) {
  switch (key) {
    case "person_name": return currentLanguage === "hi" ? "मरीज का नाम" : "Person Name";
    case "age": return currentLanguage === "hi" ? "आयु" : "Age";
    case "village": return currentLanguage === "hi" ? "गाँव" : "Village";
    case "visit_date": return currentLanguage === "hi" ? "भेंट की तिथि" : "Visit Date";
    default: return key;
  }
}

function showStatus(msg, type = "info") {
  statusMessage.textContent = msg;
  statusMessage.className = `status-box status-${type}`;
  statusMessage.classList.remove("hidden");
}

function hideStatus() {
  statusMessage.classList.add("hidden");
}

// Audio Recording & Normalization
async function toggleRecording() {
  if (mediaRecorder && mediaRecorder.state === "recording") {
    stopRecording();
  } else {
    await startRecording();
  }
}

async function startRecording() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    audioChunks = [];
    mediaRecorder = new MediaRecorder(stream);

    mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) audioChunks.push(e.data);
    };

    mediaRecorder.onstop = async () => {
      const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
      clearInterval(recordTimerInterval);
      recordingTimer.classList.add("hidden");
      audioWaveContainer.classList.add("hidden");
      recordBtn.classList.remove("btn-recording");
      recordText.textContent = I18N[currentLanguage].record_start;

      stream.getTracks().forEach((track) => track.stop());

      if (isClarifyingField) {
        await submitClarificationAudio(isClarifyingField, audioBlob);
      } else {
        await submitFullAudio(audioBlob);
      }
    };

    mediaRecorder.start();
    recordStartTime = Date.now();
    recordBtn.classList.add("btn-recording");
    recordText.textContent = I18N[currentLanguage].record_stop;
    recordingTimer.classList.remove("hidden");
    audioWaveContainer.classList.remove("hidden");

    recordTimerInterval = setInterval(() => {
      const elapsed = Math.floor((Date.now() - recordStartTime) / 1000);
      const mm = String(Math.floor(elapsed / 60)).padStart(2, "0");
      const ss = String(elapsed % 60).padStart(2, "0");
      recordingTimer.textContent = `${mm}:${ss} / 00:20`;

      if (elapsed >= 20) {
        stopRecording();
      }
    }, 500);

  } catch (err) {
    showStatus("Microphone access denied or unsupported: " + err.message, "error");
  }
}

function stopRecording() {
  if (mediaRecorder && mediaRecorder.state === "recording") {
    mediaRecorder.stop();
  }
}

async function startClarificationRecording(fieldKey) {
  if (!fieldKey) return;
  showStatus(`Recording spoken clarification for ${formatFieldName(fieldKey)}...`, "info");
  await startRecording();
}

// API Submission Pipelines
async function submitFullAudio(blobOrFile) {
  showStatus("Processing speech with Gnani Prisma STT...", "info");
  const formData = new FormData();
  formData.append("expected_version", currentVersion);
  formData.append("audio_file", blobOrFile, "recording.webm");

  try {
    const res = await fetch(`/api/drafts/${currentDraftId}/audio`, {
      method: "POST",
      body: formData,
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Server error");
    }

    const data = await res.json();
    transcriptContent.textContent = data.transcript.text;

    renderDraft(data.draft);
    hideStatus();

    if (data.draft.state === "NEEDS_CLARIFICATION") {
      playSpokenClarification();
    }
  } catch (err) {
    showStatus("Audio processing failed: " + err.message, "error");
  }
}

// Preset Chip Pipeline: Allows Immediate Frictionless Testing
async function runPresetScript(presetKey) {
  const script = PRESET_SCRIPTS[presetKey];
  if (!script) return;

  showStatus(`Processing sample dictation: "${script.substring(0, 35)}..."`, "info");
  const formData = new FormData();
  formData.append("expected_version", currentVersion);
  formData.append("simulated_transcript", script);

  try {
    const res = await fetch(`/api/drafts/${currentDraftId}/audio`, {
      method: "POST",
      body: formData,
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Preset processing error");
    }

    const data = await res.json();
    transcriptContent.textContent = data.transcript.text;

    renderDraft(data.draft);
    hideStatus();

    if (data.draft.state === "NEEDS_CLARIFICATION") {
      playSpokenClarification();
    }
  } catch (err) {
    showStatus("Preset run failed: " + err.message, "error");
  }
}

async function submitClarificationAudio(fieldKey, audioBlob) {
  showStatus(`Processing spoken clarification for ${formatFieldName(fieldKey)}...`, "info");
  const formData = new FormData();
  formData.append("target_field", fieldKey);
  formData.append("expected_version", currentVersion);
  formData.append("audio_file", audioBlob, "clarify.webm");

  try {
    const res = await fetch(`/api/drafts/${currentDraftId}/clarify`, {
      method: "POST",
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Clarification failed");
    }
    const updatedDraft = await res.json();
    renderDraft(updatedDraft);
    hideStatus();
  } catch (err) {
    showStatus("Clarification failed: " + err.message, "error");
  }
}

async function saveManualClarification() {
  const val = clarifyManualInput.value.trim();
  if (!val || !isClarifyingField) return;
  await saveFieldManualEdit(isClarifyingField, val);
}

async function saveFieldManualEdit(fieldKey, val) {
  if (!val || !val.trim()) return;

  const formData = new FormData();
  formData.append("target_field", fieldKey);
  formData.append("expected_version", currentVersion);
  formData.append("manual_value", val.trim());

  try {
    const res = await fetch(`/api/drafts/${currentDraftId}/clarify`, {
      method: "POST",
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Edit failed");
    }
    const updatedDraft = await res.json();
    renderDraft(updatedDraft);
  } catch (err) {
    showStatus("Failed to update field: " + err.message, "error");
  }
}

// Spoken Clarification Synthesis via Gnani Timbre
async function playSpokenClarification() {
  try {
    playTtsBtn.disabled = true;
    playTtsBtn.textContent = "🔊 Synthesizing...";
    audioWaveContainer.classList.remove("hidden");

    const res = await fetch(`/api/drafts/${currentDraftId}/speech`, { method: "POST" });
    if (!res.ok) throw new Error("TTS generation failed");

    const audioBlob = await res.blob();
    const audioUrl = URL.createObjectURL(audioBlob);
    ttsAudioPlayer.src = audioUrl;
    ttsAudioPlayer.play();

    playTtsBtn.textContent = "🔊 Playing...";
    ttsAudioPlayer.onended = () => {
      playTtsBtn.disabled = false;
      playTtsBtn.textContent = `🔊 ${I18N[currentLanguage].btn_hear_prompt}`;
      audioWaveContainer.classList.add("hidden");
    };
  } catch (err) {
    playTtsBtn.disabled = false;
    playTtsBtn.textContent = `🔊 ${I18N[currentLanguage].btn_hear_prompt}`;
    audioWaveContainer.classList.add("hidden");
    showStatus("Could not play spoken prompt: " + err.message, "error");
  }
}

// Idempotent Commit Pipeline
async function commitCurrentDraft() {
  showStatus("Verifying invariants and committing clinical record...", "info");
  const idempotencyKey = `idemp_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;

  try {
    const res = await fetch(`/api/drafts/${currentDraftId}/commit`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        expected_version: currentVersion,
        idempotency_key: idempotencyKey,
      }),
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Commit failed");
    }

    const data = await res.json();
    renderDraft(data.draft);
    savedRecordId.textContent = data.record_id;
    savedJson.textContent = JSON.stringify(data.draft, null, 2);
    committedResult.classList.remove("hidden");
    hideStatus();

    // Reload Registry Cache
    await loadCommittedRecords();
  } catch (err) {
    showStatus("Commit failed: " + err.message, "error");
  }
}

// Committed Records Registry
async function loadCommittedRecords() {
  try {
    const res = await fetch("/api/records");
    if (!res.ok) return;
    const records = await res.json();
    committedRecordsCache = records;
    registryCountPill.textContent = records.length;
    renderRegistryTable(records);
  } catch (err) {
    console.error("Failed to fetch committed records:", err);
  }
}

function renderRegistryTable(records) {
  if (!records || records.length === 0) {
    registryTableBody.innerHTML = `
      <tr>
        <td colspan="7" class="table-empty">No committed visit records found in session. Complete a form to commit.</td>
      </tr>
    `;
    return;
  }

  registryTableBody.innerHTML = records.map((r) => {
    const snap = r.snapshot || {};
    const fields = snap.fields || {};
    const name = fields.person_name ? fields.person_name.canonical_value : "—";
    const age = fields.age ? fields.age.canonical_value : "—";
    const village = fields.village ? fields.village.canonical_value : "—";
    const date = fields.visit_date ? fields.visit_date.canonical_value : "—";
    const timeFormatted = new Date(r.committed_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

    return `
      <tr>
        <td><strong class="code-record-id">${r.record_id}</strong></td>
        <td>${name}</td>
        <td>${age}</td>
        <td>${village}</td>
        <td>${date}</td>
        <td>${timeFormatted}</td>
        <td><span class="badge badge-live">Verified ✓</span></td>
      </tr>
    `;
  }).join("");
}

// Export Registry CSV & JSON
function exportRegistryCSV() {
  if (!committedRecordsCache.length) {
    showStatus("No committed records available to export", "error");
    return;
  }

  const headers = ["RecordID", "DraftID", "PatientName", "Age", "Village", "VisitDate", "CommittedAt"];
  const rows = committedRecordsCache.map((r) => {
    const f = r.snapshot.fields || {};
    return [
      r.record_id,
      r.draft_id,
      `"${f.person_name?.canonical_value || ""}"`,
      f.age?.canonical_value || "",
      `"${f.village?.canonical_value || ""}"`,
      f.visit_date?.canonical_value || "",
      r.committed_at
    ].join(",");
  });

  const csvContent = "data:text/csv;charset=utf-8," + [headers.join(","), ...rows].join("\n");
  const encodedUri = encodeURI(csvContent);
  const link = document.createElement("a");
  link.setAttribute("href", encodedUri);
  link.setAttribute("download", `sureword_committed_records_${Date.now()}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

function exportRegistryJSON() {
  if (!committedRecordsCache.length) {
    showStatus("No committed records available to export", "error");
    return;
  }

  const jsonStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(committedRecordsCache, null, 2));
  const link = document.createElement("a");
  link.setAttribute("href", jsonStr);
  link.setAttribute("download", `sureword_committed_records_${Date.now()}.json`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

// Navigation Tabs Switcher
function switchTab(targetView) {
  if (tabFormBtn) {
    tabFormBtn.classList.toggle("active", targetView === "form");
    tabFormBtn.setAttribute("aria-selected", targetView === "form" ? "true" : "false");
  }
  if (tabRegistryBtn) {
    tabRegistryBtn.classList.toggle("active", targetView === "registry");
    tabRegistryBtn.setAttribute("aria-selected", targetView === "registry" ? "true" : "false");
  }

  if (viewForm) {
    viewForm.classList.toggle("active", targetView === "form");
    viewForm.classList.toggle("hidden", targetView !== "form");
  }
  if (viewRegistry) {
    viewRegistry.classList.toggle("active", targetView === "registry");
    viewRegistry.classList.toggle("hidden", targetView !== "registry");
    if (targetView === "registry") {
      loadCommittedRecords();
    }
  }
}

// Event Listeners
function setupEventListeners() {
  langToggleBtn.addEventListener("click", toggleLanguage);

  if (tabFormBtn) tabFormBtn.addEventListener("click", () => switchTab("form"));
  if (tabRegistryBtn) tabRegistryBtn.addEventListener("click", () => switchTab("registry"));

  newDraftBtn.addEventListener("click", initNewDraft);
  recordBtn.addEventListener("click", toggleRecording);

  playTtsBtn.addEventListener("click", playSpokenClarification);
  clarifyMicBtn.addEventListener("click", () => startClarificationRecording(isClarifyingField));
  clarifySaveBtn.addEventListener("click", saveManualClarification);

  commitBtn.addEventListener("click", commitCurrentDraft);

  refreshRegistryBtn.addEventListener("click", loadCommittedRecords);
  exportCsvBtn.addEventListener("click", exportRegistryCSV);
  exportJsonBtn.addEventListener("click", exportRegistryJSON);

  const viewInRegistryBtn = document.getElementById("view-in-registry-btn");
  if (viewInRegistryBtn) {
    viewInRegistryBtn.addEventListener("click", () => switchTab("registry"));
  }
  const startNextDraftBtn = document.getElementById("start-next-draft-btn");
  if (startNextDraftBtn) {
    startNextDraftBtn.addEventListener("click", initNewDraft);
  }

  // Preset Chips
  document.querySelectorAll(".preset-chip").forEach((chip) => {
    chip.addEventListener("click", () => {
      const presetKey = chip.getAttribute("data-preset");
      runPresetScript(presetKey);
    });
  });

  // Inline Input Manual Edits
  FIELD_KEYS.forEach((key) => {
    const input = document.getElementById(`field-${key}`);
    if (input) {
      input.addEventListener("change", (e) => {
        saveFieldManualEdit(key, e.target.value);
      });
    }
  });
}

// Accessible Keyboard Shortcuts (frontend-a11y)
function setupKeyboardShortcuts() {
  window.addEventListener("keydown", (e) => {
    // Ctrl+Enter or Cmd+Enter to commit
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
      if (!commitBtn.disabled) {
        e.preventDefault();
        commitCurrentDraft();
      }
    }

    // Escape to close clarification or reset active focus
    if (e.key === "Escape") {
      if (!clarificationBanner.classList.contains("hidden")) {
        clarifyManualInput.blur();
      }
    }
  });
}
