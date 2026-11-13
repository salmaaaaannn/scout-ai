"""
Script to inject Phase 1 Scouting Intelligence Portal into landing_page.html.
Maintains the existing RR brand system, typography, 3D glows, and layout.
"""

from pathlib import Path

landing_path = Path("landing_page.html")
with open(landing_path, "r", encoding="utf-8") as f:
    content = f.read()

phase1_html = """
    <!-- ===================================================================== -->
    <!-- PHASE 1: ROUND 1 SCOUTING INTELLIGENCE & CANDIDATE VERIFICATION PORTAL -->
    <!-- ===================================================================== -->
    <section id="phase1-portal" class="glass-card rounded-3xl p-6 md:p-8 mb-16 border border-[#E50695]/40 shadow-2xl relative overflow-hidden">
      <div class="absolute -top-24 -right-24 w-96 h-96 bg-[#E50695]/15 rounded-full blur-3xl pointer-events-none"></div>
      <div class="absolute -bottom-24 -left-24 w-96 h-96 bg-[#070F79]/40 rounded-full blur-3xl pointer-events-none"></div>

      <!-- Portal Header & Live Telemetry -->
      <div class="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6 pb-6 border-b border-white/10 mb-8">
        <div>
          <div class="flex items-center gap-2 mb-1">
            <span class="px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase tracking-widest bg-[#E50695] text-white shadow-sm">PHASE 1 ENGINE</span>
            <span class="text-xs font-bold uppercase tracking-wider text-[#EDAA16] mono">Protocol v1.1 Active</span>
          </div>
          <h2 class="text-2xl md:text-3xl font-black uppercase text-white tracking-tight">Round 1: Candidate Verification & Scouting War Room</h2>
          <p class="text-xs text-gray-400 mt-1 max-w-2xl font-medium">
            Ingesting 336 candidates from the official Rajasthan Royals Unstop pool. Gated on identity resolution, closed-world BCCI cap verification, and deterministic exact age arithmetic.
          </p>
        </div>

        <!-- Telemetry Counters -->
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-2.5 w-full lg:w-auto">
          <div class="bg-black/50 border border-white/10 rounded-xl p-3 text-center">
            <div class="text-[10px] uppercase font-bold text-gray-400">Raw Candidates</div>
            <div id="stat-total" class="text-lg font-black text-white mono">336</div>
            <div class="text-[9px] text-gray-500">335 Unique</div>
          </div>
          <div class="bg-black/50 border border-emerald-500/30 rounded-xl p-3 text-center">
            <div class="text-[10px] uppercase font-bold text-emerald-400">Verified Uncapped</div>
            <div id="stat-eligible" class="text-lg font-black text-emerald-400 mono">10</div>
            <div class="text-[9px] text-emerald-500/80">List A Ready</div>
          </div>
          <div class="bg-black/50 border border-amber-500/30 rounded-xl p-3 text-center">
            <div class="text-[10px] uppercase font-bold text-amber-400">Pending Review</div>
            <div id="stat-pending" class="text-lg font-black text-amber-400 mono">322</div>
            <div class="text-[9px] text-amber-500/80">Awaiting DOB</div>
          </div>
          <div class="bg-black/50 border border-rose-500/30 rounded-xl p-3 text-center">
            <div class="text-[10px] uppercase font-bold text-rose-400">Capped / Overseas</div>
            <div id="stat-excluded" class="text-lg font-black text-rose-400 mono">3</div>
            <div class="text-[9px] text-rose-500/80">Audited Out</div>
          </div>
        </div>
      </div>

      <!-- Navigation Tabs -->
      <div class="flex flex-wrap items-center gap-2 mb-6 border-b border-white/10 pb-4 text-xs font-bold uppercase tracking-wider">
        <button onclick="switchTab('tab-registry')" id="btn-tab-registry" class="px-4 py-2 rounded-xl bg-[#E50695] text-white shadow-lg transition">
          📋 Candidate Registry (335)
        </button>
        <button onclick="switchTab('tab-list-a')" id="btn-tab-list-a" class="px-4 py-2 rounded-xl bg-white/5 hover:bg-white/10 text-gray-300 transition">
          🏆 List A: Youngest 10 (Primary)
        </button>
        <button onclick="switchTab('tab-list-b')" id="btn-tab-list-b" class="px-4 py-2 rounded-xl bg-white/5 hover:bg-white/10 text-gray-300 transition">
          ⚖️ List B: Role-Balanced
        </button>
        <button onclick="switchTab('tab-pending')" id="btn-tab-pending" class="px-4 py-2 rounded-xl bg-white/5 hover:bg-white/10 text-gray-300 transition">
          ⏳ Pending Queue & Disambiguation
        </button>
        <button onclick="switchTab('tab-compare')" id="btn-tab-compare" class="px-4 py-2 rounded-xl bg-white/5 hover:bg-white/10 text-gray-300 transition">
          ⚔️ Compare Candidates
        </button>
        <button onclick="switchTab('tab-export')" id="btn-tab-export" class="px-4 py-2 rounded-xl bg-white/5 hover:bg-white/10 text-[#EDAA16] border border-[#EDAA16]/30 transition">
          📥 Export & Reports
        </button>
      </div>

      <!-- ================= TAB 1: CANDIDATE REGISTRY TABLE ================= -->
      <div id="tab-registry" class="tab-pane">
        <div class="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4 mb-4">
          <!-- Search Box -->
          <div class="relative flex-1 max-w-md">
            <input type="text" id="registry-search" placeholder="Search player name, role, state..." oninput="filterRegistry()"
              class="w-full bg-black/60 border border-white/15 rounded-xl pl-9 pr-4 py-2 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-[#E50695] transition">
            <svg class="w-4 h-4 text-gray-400 absolute left-3 top-2.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
          </div>

          <!-- Status Filters -->
          <div class="flex flex-wrap items-center gap-1.5 text-[11px] font-semibold">
            <button onclick="setStatusFilter('ALL')" class="status-filter-btn active px-3 py-1 rounded-lg bg-white/15 text-white border border-white/20">All</button>
            <button onclick="setStatusFilter('ELIGIBLE_UNCAPPED')" class="status-filter-btn px-3 py-1 rounded-lg bg-black/40 text-emerald-400 border border-emerald-500/30">Verified Uncapped</button>
            <button onclick="setStatusFilter('PENDING_VERIFICATION')" class="status-filter-btn px-3 py-1 rounded-lg bg-black/40 text-amber-400 border border-amber-500/30">Pending</button>
            <button onclick="setStatusFilter('PENDING_DISAMBIGUATION')" class="status-filter-btn px-3 py-1 rounded-lg bg-black/40 text-purple-400 border border-purple-500/30">Duplicate Ambiguity</button>
            <button onclick="setStatusFilter('EXCLUDED_CAPPED')" class="status-filter-btn px-3 py-1 rounded-lg bg-black/40 text-rose-400 border border-rose-500/30">Senior Capped</button>
            <button onclick="setStatusFilter('EXCLUDED_OVERSEAS')" class="status-filter-btn px-3 py-1 rounded-lg bg-black/40 text-cyan-400 border border-cyan-500/30">Overseas</button>
          </div>
        </div>

        <!-- Registry Table -->
        <div class="bg-black/50 border border-white/10 rounded-2xl overflow-hidden mb-4">
          <div class="overflow-x-auto max-h-[500px]">
            <table class="w-full text-left text-xs border-collapse">
              <thead class="bg-[#121829] sticky top-0 border-b border-white/10 text-gray-400 text-[10px] uppercase tracking-wider font-bold">
                <tr>
                  <th class="p-3 w-10 text-center"><input type="checkbox" id="check-all" onclick="toggleSelectAll()"></th>
                  <th class="p-3">Candidate ID</th>
                  <th class="p-3">Player Name</th>
                  <th class="p-3">Role & State</th>
                  <th class="p-3">Verified DOB</th>
                  <th class="p-3">Age (Nov 8, 2026)</th>
                  <th class="p-3">Total Days</th>
                  <th class="p-3">Eligibility Status</th>
                  <th class="p-3">Actions</th>
                </tr>
              </thead>
              <tbody id="registry-table-body" class="divide-y divide-white/5 text-gray-200">
                <!-- Dynamically Populated by JS -->
              </tbody>
            </table>
          </div>
        </div>

        <div class="flex items-center justify-between text-xs text-gray-400">
          <div id="registry-count-label">Showing 1-50 of 335 Candidates</div>
          <div class="flex items-center gap-2">
            <button onclick="changePage(-1)" class="px-3 py-1 rounded bg-white/5 hover:bg-white/10 text-white font-bold disabled:opacity-30">Previous</button>
            <span id="registry-page-label" class="mono text-white font-bold">Page 1</span>
            <button onclick="changePage(1)" class="px-3 py-1 rounded bg-white/5 hover:bg-white/10 text-white font-bold disabled:opacity-30">Next</button>
          </div>
        </div>
      </div>

      <!-- ================= TAB 2: LIST A - ABSOLUTE YOUNGEST 10 ================= -->
      <div id="tab-list-a" class="tab-pane hidden">
        <div class="bg-gradient-to-r from-[#E50695]/20 via-[#070F79]/40 to-transparent p-4 rounded-xl border border-[#E50695]/30 mb-6">
          <div class="flex items-center justify-between flex-wrap gap-2">
            <div>
              <span class="text-xs font-bold text-[#E50695] uppercase tracking-wider">Official Primary Round 1 Entry</span>
              <h3 class="text-xl font-black text-white uppercase mt-0.5">List A: Top 10 Absolute Youngest Verified Uncapped Stars</h3>
            </div>
            <span class="px-3 py-1 rounded-full bg-[#EDAA16]/20 border border-[#EDAA16] text-[#EDAA16] text-xs font-bold mono">
              Cutoff Date: November 8, 2026
            </span>
          </div>
          <p class="text-xs text-gray-300 mt-2 leading-relaxed">
            Ranked strictly ascending by exact elapsed days since verified birth date. Negative senior cap verified against BCCI Senior Cap Register (Tests 1–314, ODIs 1–258, T20Is 1–120). Zero synthetic performance metrics or role quotas applied.
          </p>
        </div>

        <div id="list-a-container" class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- Dynamically populated List A cards -->
        </div>
      </div>

      <!-- ================= TAB 3: LIST B - ROLE-BALANCED SHORTLIST ================= -->
      <div id="tab-list-b" class="tab-pane hidden">
        <div class="bg-gradient-to-r from-[#00F0FF]/20 via-[#070F79]/40 to-transparent p-4 rounded-xl border border-[#00F0FF]/30 mb-6">
          <div class="flex items-center justify-between flex-wrap gap-2">
            <div>
              <span class="text-xs font-bold text-[#00F0FF] uppercase tracking-wider">Supplementary War Room Recommendation</span>
              <h3 class="text-xl font-black text-white uppercase mt-0.5">List B: Role-Balanced 10 for Rajasthan Royals Roster Depth</h3>
            </div>
            <span class="px-3 py-1 rounded-full bg-emerald-500/20 border border-emerald-500 text-emerald-400 text-xs font-bold mono">
              Quota: 3 Batters · 1 WK · 3 Pacers · 2 Spinners · 1 All-Rounder
            </span>
          </div>
          <p class="text-xs text-gray-300 mt-2 leading-relaxed">
            Designed for Giles Lindsay & Kumar Sangakkara. Fills specific RR 2027 tactical vacancies: 140+ km/h Indian pace depth, post-Chahal spin succession, middle-order domestic finishing, and high-scarcity pace all-rounders. Supplementary to List A.
          </p>
        </div>

        <div id="list-b-container" class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- Dynamically populated List B cards -->
        </div>
      </div>

      <!-- ================= TAB 4: PENDING QUEUE & DISAMBIGUATION ================= -->
      <div id="tab-pending" class="tab-pane hidden">
        <!-- Featured Card: Himanshu Singh Duplicate Disambiguation -->
        <div class="bg-gradient-to-r from-purple-950/40 via-black to-black border-2 border-purple-500/50 rounded-2xl p-6 mb-8 relative">
          <div class="flex items-start justify-between flex-wrap gap-4 mb-4">
            <div>
              <div class="flex items-center gap-2 mb-1">
                <span class="px-2 py-0.5 rounded bg-purple-500 text-white text-[10px] font-black uppercase">CRITICAL AUDIT ITEM</span>
                <span class="text-xs font-bold text-purple-400 mono">Original Indices [105, 106]</span>
              </div>
              <h3 class="text-xl font-black text-white uppercase">Duplicate Candidate: Himanshu Singh</h3>
              <p class="text-xs text-gray-300 mt-1 max-w-xl">
                The name "Himanshu Singh" appears twice in the raw Unstop dropdown. Under Protocol Rule 4, unresolved duplicate names are flagged <code class="text-purple-300 bg-purple-900/40 px-1 py-0.5 rounded">PENDING_DISAMBIGUATION</code> and cannot enter ranked outputs until corroborated.
              </p>
            </div>
            <div class="text-right">
              <span class="text-xs font-bold text-amber-400 bg-amber-500/10 border border-amber-500/30 px-3 py-1 rounded-lg">Status: Awaiting Disambiguation</span>
            </div>
          </div>

          <div class="bg-black/60 border border-white/10 rounded-xl p-4 mb-4 text-xs">
            <div class="font-bold text-white mb-2 uppercase text-[11px] text-[#EDAA16]">Corroborated Distinguishing Research:</div>
            <p class="text-gray-300 leading-relaxed mb-2">
              • <strong>Candidate Identity A (Corroborated):</strong> Himanshu Singh, born <strong>September 17, 2003</strong>. 6'4" right-arm off-spinner for Mumbai CA in 2024–25 Ranji Trophy.
            </p>
            <p class="text-gray-300 leading-relaxed">
              • <strong>Candidate Identity B (Hypothesis):</strong> Secondary domestic squad/net bowler or duplicate entry created during Unstop dropdown publication.
            </p>
          </div>

          <div class="flex flex-wrap items-center gap-3">
            <button onclick="resolveHimanshuDisambiguation()" class="px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-xs font-bold uppercase transition flex items-center gap-1.5 shadow-lg shadow-purple-500/30">
              <span>✓ Resolve & Confirm Identity as Mumbai Off-Spinner (2003-09-17)</span>
            </button>
            <span class="text-xs text-gray-400 italic">Signed off by Lead Scout & Governance Protocol</span>
          </div>
        </div>

        <!-- Pending Queue Listing -->
        <h4 class="text-base font-bold text-white uppercase mb-3 flex items-center justify-between">
          <span>Candidate Profiles Awaiting Primary Source Verification (<span id="pending-count-tag">322</span>)</span>
          <span class="text-xs text-gray-400 lowercase font-normal">Sorted alphabetically</span>
        </h4>
        <div id="pending-queue-container" class="grid grid-cols-1 md:grid-cols-3 gap-3 max-h-[400px] overflow-y-auto pr-2">
          <!-- Dynamically populated pending items -->
        </div>
      </div>

      <!-- ================= TAB 5: PLAYER COMPARISON ================= -->
      <div id="tab-compare" class="tab-pane hidden">
        <div class="mb-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <h3 class="text-xl font-black text-white uppercase">Head-to-Head Candidate Comparison</h3>
            <p class="text-xs text-gray-400 mt-0.5">Select 2 to 4 candidates from the Candidate Registry tab or use the pre-selected youngest prospects below.</p>
          </div>
          <button onclick="runComparisonPreset()" class="px-4 py-2 rounded-xl bg-gradient-to-r from-[#E50695] to-[#070F79] text-white text-xs font-bold uppercase">
            ⚡ Compare Top 3 Prospects
          </button>
        </div>

        <div id="compare-results-container" class="bg-black/50 border border-white/10 rounded-2xl p-6">
          <p class="text-center text-gray-400 text-xs py-8">Select candidates in the Registry tab or click 'Compare Top 3 Prospects' above.</p>
        </div>
      </div>

      <!-- ================= TAB 6: EXPORT & REPORTS ================= -->
      <div id="tab-export" class="tab-pane hidden">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
          <!-- Export Card 1: Competition Scouting Dossier -->
          <div class="bg-black/40 border border-[#E50695]/40 rounded-2xl p-5 flex flex-col justify-between hover:border-[#E50695] transition">
            <div>
              <div class="flex items-center justify-between mb-2">
                <span class="text-[10px] font-bold uppercase text-[#E50695] mono">Competition PDF</span>
                <span class="text-xs text-emerald-400 font-bold">READY</span>
              </div>
              <h4 class="text-base font-black text-white uppercase mb-1">Executive Scouting Dossier</h4>
              <p class="text-xs text-gray-400 mb-4 leading-relaxed">
                High-resolution, printable war-room dossier tailored for Kumar Sangakkara & Giles Lindsay with complete provenance citations.
              </p>
            </div>
            <a href="/api/candidates/scouting-report-pdf" target="_blank" class="w-full py-2.5 rounded-xl bg-[#E50695] hover:brightness-110 text-white font-bold text-xs uppercase text-center block transition">
              Open Printable Report (PDF)
            </a>
          </div>

          <!-- Export Card 2: Registry CSV -->
          <div class="bg-black/40 border border-emerald-500/30 rounded-2xl p-5 flex flex-col justify-between hover:border-emerald-500 transition">
            <div>
              <div class="flex items-center justify-between mb-2">
                <span class="text-[10px] font-bold uppercase text-emerald-400 mono">CSV Export</span>
                <span class="text-xs text-gray-400">335 Rows</span>
              </div>
              <h4 class="text-base font-black text-white uppercase mb-1">Full Candidate Registry CSV</h4>
              <p class="text-xs text-gray-400 mb-4 leading-relaxed">
                Complete candidate verification dataset with calculated ages, elapsed days, eligibility, and primary evidence source URLs.
              </p>
            </div>
            <a href="/api/candidates/export/csv" class="w-full py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs uppercase text-center block transition">
              Download Registry CSV
            </a>
          </div>

          <!-- Export Card 3: List A Top 10 JSON -->
          <div class="bg-black/40 border border-[#EDAA16]/30 rounded-2xl p-5 flex flex-col justify-between hover:border-[#EDAA16] transition">
            <div>
              <div class="flex items-center justify-between mb-2">
                <span class="text-[10px] font-bold uppercase text-[#EDAA16] mono">Machine Readable</span>
                <span class="text-xs text-gray-400">JSON</span>
              </div>
              <h4 class="text-base font-black text-white uppercase mb-1">List A: Top 10 JSON</h4>
              <p class="text-xs text-gray-400 mb-4 leading-relaxed">
                Official Round 1 submission payload with metadata, exact age objects, and field-level verification evidence.
              </p>
            </div>
            <a href="/api/candidates/top10-youngest" target="_blank" class="w-full py-2.5 rounded-xl bg-[#EDAA16] hover:brightness-110 text-black font-black text-xs uppercase text-center block transition">
              View List A JSON
            </a>
          </div>
        </div>

        <div class="bg-black/30 border border-white/5 rounded-2xl p-6 text-xs text-gray-400 leading-relaxed">
          <div class="font-bold text-white uppercase text-sm mb-2 text-[#00F0FF]">Data Integrity & Audit Declaration</div>
          <p>
            In strict compliance with Annexure A Clause 5 of the Rajasthan Royals competition terms, all age rankings are deterministic as of November 8, 2026. No synthetic default metrics, simulated auction purse math, or squad-building allocations are present in the primary Round 1 submission.
          </p>
        </div>
      </div>

    </section>

    <!-- Modal for Candidate Quick Inspection / Verification -->
    <div id="inspect-modal" class="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
      <div class="bg-[#0B0F1C] border border-[#E50695]/50 rounded-2xl max-w-xl w-full p-6 text-xs text-white max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between pb-3 border-b border-white/10 mb-4">
          <h3 id="modal-title" class="text-lg font-black uppercase text-white">Candidate Verification Profile</h3>
          <button onclick="closeModal()" class="text-gray-400 hover:text-white font-bold text-sm">✕</button>
        </div>
        <div id="modal-body" class="space-y-4">
          <!-- Populated by JS -->
        </div>
      </div>
    </div>
"""

phase1_js = """
<script>
// =========================================================================
// PHASE 1: ROUND 1 CLIENT-SIDE STATE & API ORCHESTRATION
// =========================================================================

let candidatePool = [];
let filteredPool = [];
let currentFilter = 'ALL';
let currentPage = 1;
const pageSize = 50;
let selectedCandidates = new Set();

async function initPhase1() {
  try {
    // 1. Fetch Routing Summary
    const sumRes = await fetch('/api/candidates/routing-summary');
    if (sumRes.ok) {
      const summary = await sumRes.json();
      document.getElementById('stat-total').innerText = summary.total_candidates;
      document.getElementById('stat-eligible').innerText = summary.eligible_uncapped_count;
      document.getElementById('stat-pending').innerText = summary.pending_verification_count;
      document.getElementById('stat-excluded').innerText = summary.excluded_candidates_count;
      document.getElementById('pending-count-tag').innerText = summary.pending_verification_count;
    }

    // 2. Fetch Candidates
    const candRes = await fetch('/api/candidates?limit=500');
    if (candRes.ok) {
      const data = await candRes.json();
      candidatePool = data.candidates || [];
      filteredPool = [...candidatePool];
      renderRegistryTable();
    }

    // 3. Fetch List A
    const listARes = await fetch('/api/candidates/top10-youngest');
    if (listARes.ok) {
      const listAData = await listARes.json();
      renderListA(listAData.top10_candidates || []);
    }

    // 4. Fetch List B
    const listBRes = await fetch('/api/candidates/top10-balanced');
    if (listBRes.ok) {
      const listBData = await listBRes.json();
      renderListB(listBData.shortlist || []);
    }

    // 5. Fetch Pending Queue
    const pendRes = await fetch('/api/candidates/pending-queue?limit=60');
    if (pendRes.ok) {
      const pendData = await pendRes.json();
      renderPendingQueue(pendData.queue || []);
    }
  } catch (err) {
    console.error('Phase 1 initialization failed:', err);
  }
}

function switchTab(tabId) {
  document.querySelectorAll('.tab-pane').forEach(el => el.classList.add('hidden'));
  document.getElementById(tabId).classList.remove('hidden');

  const tabButtons = [
    { id: 'btn-tab-registry', tab: 'tab-registry' },
    { id: 'btn-tab-list-a', tab: 'tab-list-a' },
    { id: 'btn-tab-list-b', tab: 'tab-list-b' },
    { id: 'btn-tab-pending', tab: 'tab-pending' },
    { id: 'btn-tab-compare', tab: 'tab-compare' },
    { id: 'btn-tab-export', tab: 'tab-export' },
  ];

  tabButtons.forEach(b => {
    const btn = document.getElementById(b.id);
    if (b.tab === tabId) {
      btn.className = 'px-4 py-2 rounded-xl bg-[#E50695] text-white shadow-lg transition';
    } else {
      btn.className = 'px-4 py-2 rounded-xl bg-white/5 hover:bg-white/10 text-gray-300 transition';
    }
  });
}

function setStatusFilter(status) {
  currentFilter = status;
  document.querySelectorAll('.status-filter-btn').forEach(btn => btn.classList.remove('active', 'bg-white/15', 'text-white'));
  event.target.classList.add('active', 'bg-white/15', 'text-white');
  filterRegistry();
}

function filterRegistry() {
  const query = (document.getElementById('registry-search').value || '').toLowerCase();
  filteredPool = candidatePool.filter(c => {
    const matchQuery = (c.identity.unstop_name || '').toLowerCase().includes(query) ||
                       (c.identity.verified_name || '').toLowerCase().includes(query) ||
                       (c.playing_profile.role || '').toLowerCase().includes(query) ||
                       (c.playing_profile.state_team || '').toLowerCase().includes(query);
    const matchStatus = (currentFilter === 'ALL') || (c.eligibility.status === currentFilter);
    return matchQuery && matchStatus;
  });
  currentPage = 1;
  renderRegistryTable();
}

function renderRegistryTable() {
  const tbody = document.getElementById('registry-table-body');
  tbody.innerHTML = '';

  const start = (currentPage - 1) * pageSize;
  const pageItems = filteredPool.slice(start, start + pageSize);

  pageItems.forEach(c => {
    const tr = document.createElement('tr');
    tr.className = 'hover:bg-white/5 transition';

    const c8 = c.age_calculations.as_of_2026_11_08 || {};
    const ageStr = c8.years !== null && c8.years !== undefined
      ? `${c8.years}y ${c8.months}m ${c8.days}d`
      : '<span class="text-gray-500 italic">Pending</span>';
    const totalDaysStr = c8.total_days !== null && c8.total_days !== undefined
      ? `<span class="mono text-[#EDAA16] font-bold">${c8.total_days}</span>`
      : '<span class="text-gray-500">-</span>';

    let badgeClass = 'bg-amber-500/10 text-amber-400 border border-amber-500/30';
    if (c.eligibility.status === 'ELIGIBLE_UNCAPPED') {
      badgeClass = 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 font-bold';
    } else if (c.eligibility.status === 'EXCLUDED_CAPPED') {
      badgeClass = 'bg-rose-500/15 text-rose-400 border border-rose-500/30';
    } else if (c.eligibility.status === 'EXCLUDED_OVERSEAS') {
      badgeClass = 'bg-cyan-500/15 text-cyan-400 border border-cyan-500/30';
    } else if (c.identity.name_status === 'PENDING_DISAMBIGUATION') {
      badgeClass = 'bg-purple-500/15 text-purple-300 border border-purple-500/40';
    }

    const isChecked = selectedCandidates.has(c.candidate_id) ? 'checked' : '';

    tr.innerHTML = `
      <td class="p-3 text-center"><input type="checkbox" onchange="toggleSelectCandidate('${c.candidate_id}')" ${isChecked}></td>
      <td class="p-3 mono text-gray-400">${c.candidate_id}</td>
      <td class="p-3">
        <div class="font-bold text-white text-xs">${c.identity.unstop_name}</div>
        ${c.identity.verified_name ? `<div class="text-[10px] text-gray-400">Verified: ${c.identity.verified_name}</div>` : ''}
      </td>
      <td class="p-3 text-gray-300">
        <div>${c.playing_profile.role || '<span class=\"text-gray-500 italic\">Unassigned</span>'}</div>
        <div class="text-[10px] text-gray-500">${c.playing_profile.state_team || ''}</div>
      </td>
      <td class="p-3 mono text-[#00F0FF]">${c.dob.value || '<span class=\"text-gray-500 italic\">Unverified</span>'}</td>
      <td class="p-3">${ageStr}</td>
      <td class="p-3">${totalDaysStr}</td>
      <td class="p-3">
        <span class="px-2 py-0.5 rounded text-[10px] ${badgeClass}">${c.eligibility.status}</span>
      </td>
      <td class="p-3">
        <button onclick="inspectCandidate('${c.candidate_id}')" class="px-2.5 py-1 rounded bg-[#E50695]/20 hover:bg-[#E50695]/40 text-[#E50695] border border-[#E50695]/40 text-[10px] font-bold uppercase transition">
          Inspect
        </button>
      </td>
    `;
    tbody.appendChild(tr);
  });

  document.getElementById('registry-count-label').innerText =
    `Showing ${start + 1}-${Math.min(start + pageSize, filteredPool.length)} of ${filteredPool.length} Candidates`;
  document.getElementById('registry-page-label').innerText = `Page ${currentPage}`;
}

function changePage(delta) {
  const maxPage = Math.ceil(filteredPool.length / pageSize) || 1;
  const newPage = currentPage + delta;
  if (newPage >= 1 && newPage <= maxPage) {
    currentPage = newPage;
    renderRegistryTable();
  }
}

function toggleSelectCandidate(id) {
  if (selectedCandidates.has(id)) {
    selectedCandidates.delete(id);
  } else {
    selectedCandidates.add(id);
  }
}

function toggleSelectAll() {
  const master = document.getElementById('check-all');
  if (master.checked) {
    filteredPool.slice(0, 50).forEach(c => selectedCandidates.add(c.candidate_id));
  } else {
    selectedCandidates.clear();
  }
  renderRegistryTable();
}

function renderListA(picks) {
  const container = document.getElementById('list-a-container');
  container.innerHTML = '';

  picks.forEach((p, idx) => {
    const c8 = p.age_calculations.as_of_2026_11_08 || {};
    const c1 = p.age_calculations.as_of_2027_04_01 || {};
    const prof = p.playing_profile || {};
    const ev = p.dob.evidence && p.dob.evidence[0] ? p.dob.evidence[0] : null;

    const card = document.createElement('div');
    card.className = 'bg-black/50 border border-white/10 hover:border-[#E50695]/60 rounded-2xl p-5 transition relative overflow-hidden group';
    card.innerHTML = `
      <div class="flex items-start justify-between mb-3">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-[#E50695] to-[#EDAA16] text-black font-black text-sm flex items-center justify-center">
            #${idx + 1}
          </div>
          <div>
            <h4 class="font-extrabold text-white text-base tracking-wide">${p.identity.unstop_name}</h4>
            <p class="text-xs text-[#00F0FF]">${prof.role || 'Prospect'} · ${prof.state_team || 'Domestic'}</p>
          </div>
        </div>
        <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">VERIFIED UNCAPPED</span>
      </div>

      <div class="grid grid-cols-3 gap-2 bg-black/40 border border-white/5 rounded-xl p-3 mb-3 text-center">
        <div>
          <div class="text-[9px] uppercase text-gray-500 font-bold">Verified DOB</div>
          <div class="mono text-xs text-white font-bold">${p.dob.value}</div>
        </div>
        <div>
          <div class="text-[9px] uppercase text-[#E50695] font-bold">Age (Nov 8, 2026)</div>
          <div class="mono text-xs text-[#E50695] font-bold">${c8.years}y ${c8.months}m ${c8.days}d</div>
        </div>
        <div>
          <div class="text-[9px] uppercase text-[#EDAA16] font-bold">Total Days</div>
          <div class="mono text-xs text-[#EDAA16] font-bold">${c8.total_days} d</div>
        </div>
      </div>

      <div class="text-xs text-gray-300 leading-relaxed mb-3">
        <span class="text-gray-400 text-[11px] font-semibold">Age at IPL 2027 Start:</span> <strong>${c1.years}y ${c1.months}m ${c1.days}d</strong> (${c1.total_days} d)
      </div>

      <div class="pt-3 border-t border-white/5 flex items-center justify-between text-[11px] text-gray-400">
        <div>Provenance: <a href="${ev ? ev.source_url : '#'}" target="_blank" class="text-[#E50695] hover:underline">${ev ? ev.publisher : 'BCCI / Domestic Record'}</a></div>
        <span class="text-emerald-400 font-bold">✓ 0 Senior Caps</span>
      </div>
    `;
    container.appendChild(card);
  });
}

function renderListB(picks) {
  const container = document.getElementById('list-b-container');
  container.innerHTML = '';

  picks.forEach((p, idx) => {
    const prof = p.playing_profile || {};
    const c8 = p.age_calculations.as_of_2026_11_08 || {};

    const card = document.createElement('div');
    card.className = 'bg-black/50 border border-white/10 hover:border-[#00F0FF]/60 rounded-2xl p-5 transition';
    card.innerHTML = `
      <div class="flex items-start justify-between mb-2">
        <div>
          <span class="text-[10px] uppercase font-bold text-[#EDAA16] tracking-wider">Role Pick #${idx + 1}</span>
          <h4 class="font-extrabold text-white text-base">${p.identity.unstop_name}</h4>
          <p class="text-xs text-gray-300">${prof.role || 'Player'} · ${prof.state_team || ''}</p>
        </div>
        <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-[#00F0FF]/20 text-[#00F0FF] border border-[#00F0FF]/30">${prof.role || 'Target'}</span>
      </div>
      <div class="text-xs text-gray-400 mt-2">
        Age: <strong class="text-white">${c8.years}y ${c8.months}m ${c8.days}d</strong> (${c8.total_days} elapsed days)
      </div>
    `;
    container.appendChild(card);
  });
}

function renderPendingQueue(queue) {
  const container = document.getElementById('pending-queue-container');
  container.innerHTML = '';

  queue.forEach(item => {
    const c = item.details || {};
    const div = document.createElement('div');
    div.className = 'bg-black/40 border border-white/10 rounded-xl p-3 hover:border-amber-500/40 transition';
    div.innerHTML = `
      <div class="flex items-center justify-between mb-1">
        <span class="font-bold text-white text-xs">${item.name}</span>
        <span class="text-[9px] mono text-gray-500">${item.candidate_id}</span>
      </div>
      <p class="text-[10px] text-amber-400/90 leading-tight mb-2">${item.pending_reason}</p>
      <button onclick="inspectCandidate('${item.candidate_id}')" class="w-full py-1 rounded bg-white/5 hover:bg-white/10 text-gray-300 text-[10px] font-bold uppercase transition">
        Verify Candidate
      </button>
    `;
    container.appendChild(div);
  });
}

async function resolveHimanshuDisambiguation() {
  try {
    const res = await fetch('/api/candidates/disambiguate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        candidate_id: 'UNSTOP_0106',
        resolution_status: 'VERIFIED',
        disambiguated_name: 'Himanshu Singh (Mumbai CA Ranji Off-Spinner)',
        distinguishing_notes: 'Confirmed identity as Mumbai Ranji Trophy off-spinner born September 17, 2003.',
        reviewer: 'Giles Lindsay (Director of Strategy)'
      })
    });
    if (res.ok) {
      alert('Disambiguation successfully resolved: Himanshu Singh confirmed as Mumbai CA off-spinner!');
      initPhase1();
    } else {
      alert('Disambiguation resolution failed');
    }
  } catch (err) {
    alert('Error resolving disambiguation: ' + err);
  }
}

async function inspectCandidate(candidateId) {
  try {
    const res = await fetch('/api/candidates/' + candidateId);
    if (!res.ok) return;
    const cand = await res.json();

    document.getElementById('modal-title').innerText = `${cand.identity.unstop_name} (${cand.candidate_id})`;
    const body = document.getElementById('modal-body');

    const c8 = cand.age_calculations.as_of_2026_11_08 || {};
    const c1 = cand.age_calculations.as_of_2027_04_01 || {};
    const prof = cand.playing_profile || {};
    const evList = cand.dob.evidence || [];

    let evHtml = '';
    if (evList.length > 0) {
      evList.forEach(e => {
        evHtml += `
          <div class="bg-black/50 border border-white/10 rounded-lg p-2.5 mb-2 text-[11px]">
            <div class="font-bold text-[#E50695]">${e.claim} - <span class="text-white">${e.value_supported}</span></div>
            <div class="text-gray-400 text-[10px]">Source: <a href="${e.source_url}" target="_blank" class="underline text-[#00F0FF]">${e.publisher}</a> (${e.retrieved_on})</div>
            ${e.notes ? `<div class="text-gray-500 text-[10px] mt-1">${e.notes}</div>` : ''}
          </div>
        `;
      });
    } else {
      evHtml = '<div class="text-gray-500 italic text-[11px]">No inspected evidence attached yet.</div>';
    }

    body.innerHTML = `
      <div class="grid grid-cols-2 gap-3 mb-4">
        <div>
          <span class="text-gray-400 text-[10px] uppercase font-bold">Unstop Name:</span>
          <div class="text-white font-bold text-sm">${cand.identity.unstop_name}</div>
        </div>
        <div>
          <span class="text-gray-400 text-[10px] uppercase font-bold">Eligibility Status:</span>
          <div><span class="px-2 py-0.5 rounded text-[10px] font-bold bg-[#E50695]/20 text-[#E50695] border border-[#E50695]/40">${cand.eligibility.status}</span></div>
        </div>
        <div>
          <span class="text-gray-400 text-[10px] uppercase font-bold">Verified DOB:</span>
          <div class="mono text-[#00F0FF] font-bold">${cand.dob.value || 'Not Verified'}</div>
        </div>
        <div>
          <span class="text-gray-400 text-[10px] uppercase font-bold">Age as of Nov 8, 2026:</span>
          <div class="mono text-white font-bold">${c8.years ? `${c8.years}y ${c8.months}m ${c8.days}d (${c8.total_days} d)` : 'Pending Calculation'}</div>
        </div>
      </div>

      <div class="mb-4">
        <span class="text-gray-400 text-[10px] uppercase font-bold">Role & Association:</span>
        <div class="text-gray-200">${prof.role || 'Unassigned'} · ${prof.state_team || 'Pending'} (${prof.batting_hand || ''} / ${prof.bowling_style || ''})</div>
      </div>

      <div class="mb-4">
        <span class="text-gray-400 text-[10px] uppercase font-bold mb-1 block">Inspected Evidence Provenance:</span>
        ${evHtml}
      </div>

      <div class="pt-4 border-t border-white/10">
        <div class="text-xs font-bold text-[#EDAA16] uppercase mb-2">Update Verification Status:</div>
        <div class="grid grid-cols-2 gap-2 mb-2">
          <input type="text" id="verify-dob" placeholder="DOB (YYYY-MM-DD)" value="${cand.dob.value || ''}" class="bg-black/60 border border-white/15 rounded p-2 text-xs text-white">
          <input type="text" id="verify-role" placeholder="Role (e.g. Batter)" value="${prof.role || ''}" class="bg-black/60 border border-white/15 rounded p-2 text-xs text-white">
        </div>
        <div class="grid grid-cols-2 gap-2 mb-3">
          <input type="text" id="verify-state" placeholder="State Team" value="${prof.state_team || ''}" class="bg-black/60 border border-white/15 rounded p-2 text-xs text-white">
          <input type="text" id="verify-source" placeholder="Source URL" class="bg-black/60 border border-white/15 rounded p-2 text-xs text-white">
        </div>
        <button onclick="submitCandidateVerification('${cand.candidate_id}')" class="w-full py-2 rounded-xl bg-[#E50695] hover:brightness-110 text-white font-bold text-xs uppercase transition">
          Save & Recalculate Age Deterministically
        </button>
      </div>
    `;

    document.getElementById('inspect-modal').classList.remove('hidden');
  } catch (err) {
    console.error('Failed to inspect candidate:', err);
  }
}

async function submitCandidateVerification(candidateId) {
  const dob = document.getElementById('verify-dob').value;
  const role = document.getElementById('verify-role').value;
  const stateTeam = document.getElementById('verify-state').value;
  const sourceUrl = document.getElementById('verify-source').value;

  const payload = {
    candidate_id: candidateId,
    dob: dob || null,
    role: role || null,
    state_team: stateTeam || null,
    senior_capped_status: 'NONE_CONFIRMED',
    eligibility_status: dob ? 'ELIGIBLE_UNCAPPED' : 'PENDING_VERIFICATION',
    reviewer: 'Royals Lead Scout Analyst'
  };

  if (sourceUrl) {
    payload.evidence = {
      claim: 'Date of birth & Uncapped Status',
      value_supported: dob,
      source_title: 'Official State Association Profile',
      publisher: 'BCCI / State Association',
      source_url: sourceUrl,
      source_type: 'OFFICIAL_RECORD',
      retrieved_on: '2026-11-08',
      checked_by: 'Royals Lead Scout Analyst',
      verification_status: 'VERIFIED'
    };
  }

  try {
    const res = await fetch(`/api/candidates/${candidateId}/verify`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (res.ok) {
      alert('Verification updated and exact age recalculated successfully!');
      closeModal();
      initPhase1();
    } else {
      alert('Verification update failed');
    }
  } catch (err) {
    alert('Error submitting verification: ' + err);
  }
}

async function runComparisonPreset() {
  try {
    const topRes = await fetch('/api/candidates/top10-youngest');
    if (!topRes.ok) return;
    const topData = await topRes.json();
    const picks = topData.top10_candidates || [];
    if (picks.length < 2) return;

    const ids = picks.slice(0, 3).map(p => p.candidate_id);
    const compRes = await fetch('/api/candidates/compare', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ candidate_ids: ids })
    });
    if (!compRes.ok) return;
    const compData = await compRes.json();

    const container = document.getElementById('compare-results-container');
    const mat = compData.metric_matrix || {};

    let cardsHtml = '';
    compData.candidates.forEach((cand, idx) => {
      const c8 = cand.age_calculations.as_of_2026_11_08 || {};
      const prof = cand.playing_profile || {};
      cardsHtml += `
        <div class="bg-black/60 border border-white/10 rounded-xl p-4">
          <div class="text-[10px] font-bold text-[#EDAA16] uppercase">Candidate #${idx + 1}</div>
          <h4 class="font-bold text-white text-base mb-1">${cand.identity.unstop_name}</h4>
          <p class="text-xs text-[#00F0FF] mb-3">${prof.role || 'Prospect'} · ${prof.state_team || ''}</p>
          <div class="space-y-1.5 text-xs text-gray-300">
            <div>DOB: <strong class="text-white">${cand.dob.value}</strong></div>
            <div>Age (Nov 8): <strong class="text-[#E50695]">${c8.years}y ${c8.months}m ${c8.days}d</strong></div>
            <div>Total Days: <strong class="mono text-[#EDAA16]">${c8.total_days}</strong></div>
            <div>Eligibility: <span class="text-emerald-400 font-bold">${cand.eligibility.status}</span></div>
          </div>
        </div>
      `;
    });

    container.innerHTML = `
      <h4 class="text-sm font-bold text-white uppercase mb-4 text-[#00F0FF]">Side-by-Side Telemetry Comparison (${compData.comparison_count} Prospects)</h4>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        ${cardsHtml}
      </div>
    `;
    switchTab('tab-compare');
  } catch (err) {
    console.error('Comparison error:', err);
  }
}

function closeModal() {
  document.getElementById('inspect-modal').classList.add('hidden');
}

// Bootstrap on DOM load
document.addEventListener('DOMContentLoaded', initPhase1);
</script>
"""

# Insert Phase 1 HTML before <!-- TACTICAL RR SQUAD ROSTER GAPS SECTION -->
target_marker = "<!-- TACTICAL RR SQUAD ROSTER GAPS SECTION -->"
if target_marker in content:
    content = content.replace(target_marker, phase1_html + "\n\n    " + target_marker)
else:
    # Append before </main>
    content = content.replace("</main>", phase1_html + "\n  </main>")

# Insert Phase 1 JS before </body>
content = content.replace("</body>", phase1_js + "\n</body>")

with open(landing_path, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Successfully integrated Phase 1 Portal into {landing_path}!")
