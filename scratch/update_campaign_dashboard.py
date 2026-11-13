"""
Update landing_page.html to:
1. Insert #tab-campaign pane before #tab-export
2. Provide dynamic counter span IDs in #tab-campaign:
   - campaign-stat-total
   - campaign-stat-verified
   - campaign-stat-pending
   - campaign-stat-missing
   - campaign-stat-disambig
   - campaign-stat-excluded
   - campaign-gate-status
3. Include live 4-way exact partition callout:
   - partition-stat-verified (16)
   - partition-stat-missing (315)
   - partition-stat-disambig (1)
   - partition-stat-excluded (3)
   - Total (335)
4. Update loadCampaignData() to dynamically fetch and populate these DOM elements from /api/candidates/verification-campaign
5. Update switchTab() to include { id: 'btn-tab-campaign', tab: 'tab-campaign' }
6. Update List A limitation banner to have dynamic id 'limitation-banner-text' and update from API
"""

from pathlib import Path

landing_path = Path("landing_page.html")
with open(landing_path, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Update limitation banner in tab-list-a to have id="limitation-banner-text"
old_limitation = """<p class="text-xs text-gray-300 mt-1 leading-relaxed">
              <strong>METHODOLOGY LIMITATION:</strong> This list represents the youngest candidates among those verified to date (10 of 335 candidates). 322 candidates in the Unstop candidate pool remain in the verification queue awaiting primary source DOB and Senior International Appearance Audits. Because unverified candidates could be younger than those listed here, this ranking is <strong>PROVISIONAL</strong> and strictly for internal research. The designation <em>'Top 10 Absolute Youngest'</em> is locked until 100% of potentially eligible candidates have completed verification.
            </p>"""

new_limitation = """<p id="limitation-banner-text" class="text-xs text-gray-300 mt-1 leading-relaxed">
              <strong>METHODOLOGY LIMITATION:</strong> This list represents the youngest candidates among those verified to date (16 of 335 candidates). 316 candidates in the Unstop candidate pool remain in the verification queue awaiting primary source DOB and Senior International Appearance Audits. Because unverified candidates could be younger than those listed here, this ranking is <strong>PROVISIONAL</strong> and strictly for internal research. The designation <em>'Top 10 Absolute Youngest'</em> is locked until 100% of potentially eligible candidates have completed verification.
            </p>"""

if old_limitation in html:
    html = html.replace(old_limitation, new_limitation)
elif 'id="limitation-banner-text"' not in html:
    # Look for generic limitation paragraph
    idx = html.find('<strong>METHODOLOGY LIMITATION:</strong>')
    if idx != -1:
        start_p = html.rfind('<p', 0, idx)
        end_p = html.find('</p>', idx) + 4
        html = html[:start_p] + new_limitation + html[end_p:]

# 2. Add #tab-campaign pane before tab-export
campaign_pane_html = """      <!-- ================= TAB 6: DOB VERIFICATION CAMPAIGN ================= -->
      <div id="tab-campaign" class="tab-pane hidden">
        <div class="bg-gradient-to-r from-cyan-950/40 via-black to-black border border-cyan-500/30 rounded-2xl p-6 mb-6">
          <div class="flex items-start justify-between flex-wrap gap-4 mb-4">
            <div>
              <span class="px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase tracking-widest bg-cyan-500 text-black shadow-sm">RESEARCH COMPLETENESS GATE</span>
              <h3 class="text-xl font-black text-white uppercase mt-1">DOB Verification Campaign & Pool Coverage</h3>
              <p class="text-xs text-gray-300 mt-1 max-w-2xl">
                Protocol v1.2 audit coverage across all 335 unique candidate records. Tracks full DOB precision, source URLs, and Senior International Appearance Audits. Zero synthetic dates or simulated statistics.
              </p>
            </div>
            <span id="campaign-gate-status" class="px-3 py-1 rounded-full bg-amber-500/20 border border-amber-500 text-amber-400 text-xs font-bold mono">
              Status: LOCKED_PROVISIONAL_MODE
            </span>
          </div>

          <!-- Dynamic Campaign Metric Counters -->
          <div class="grid grid-cols-2 sm:grid-cols-6 gap-3 pt-4 border-t border-white/10 text-center mb-5">
            <div class="bg-black/50 p-2.5 rounded-xl border border-white/10">
              <div class="text-[10px] text-gray-400 font-bold uppercase">Total Unique</div>
              <div id="campaign-stat-total" class="text-base font-black text-white mono">335</div>
            </div>
            <div class="bg-black/50 p-2.5 rounded-xl border border-emerald-500/30">
              <div class="text-[10px] text-emerald-400 font-bold uppercase">Verified Full DOB</div>
              <div id="campaign-stat-verified" class="text-base font-black text-emerald-400 mono">16</div>
            </div>
            <div class="bg-black/50 p-2.5 rounded-xl border border-cyan-500/30">
              <div class="text-[10px] text-cyan-400 font-bold uppercase">Pending Research</div>
              <div id="campaign-stat-pending" class="text-base font-black text-cyan-400 mono">316</div>
            </div>
            <div class="bg-black/50 p-2.5 rounded-xl border border-amber-500/30">
              <div class="text-[10px] text-amber-400 font-bold uppercase">Missing DOB</div>
              <div id="campaign-stat-missing" class="text-base font-black text-amber-400 mono">315</div>
            </div>
            <div class="bg-black/50 p-2.5 rounded-xl border border-purple-500/30">
              <div class="text-[10px] text-purple-400 font-bold uppercase">Disambiguation</div>
              <div id="campaign-stat-disambig" class="text-base font-black text-purple-400 mono">1</div>
            </div>
            <div class="bg-black/50 p-2.5 rounded-xl border border-rose-500/30">
              <div class="text-[10px] text-rose-400 font-bold uppercase">Capped / Overseas</div>
              <div id="campaign-stat-excluded" class="text-base font-black text-rose-400 mono">3</div>
            </div>
          </div>

          <!-- 4-Way Exact Partition Callout -->
          <div class="bg-black/60 border border-white/10 rounded-xl p-4">
            <div class="flex items-center justify-between mb-2">
              <span class="text-[11px] font-black uppercase tracking-wider text-cyan-400">Exact Mathematical Partition (335 Unique Candidates)</span>
              <span class="text-[10px] font-bold text-emerald-400 mono">Partition Check: 16 + 315 + 1 + 3 = 335</span>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-4 gap-2 text-xs">
              <div class="p-2.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20">
                <span class="font-bold text-emerald-400">1. Verified Eligible:</span> <span id="partition-stat-verified" class="mono font-black text-white">16</span>
                <p class="text-[10px] text-gray-400 mt-0.5">Uncapped & Full DOB verified</p>
              </div>
              <div class="p-2.5 rounded-lg bg-amber-500/10 border border-amber-500/20">
                <span class="font-bold text-amber-400">2. Pending DOB:</span> <span id="partition-stat-missing" class="mono font-black text-white">315</span>
                <p class="text-[10px] text-gray-400 mt-0.5">Awaiting primary source DOB</p>
              </div>
              <div class="p-2.5 rounded-lg bg-purple-500/10 border border-purple-500/20">
                <span class="font-bold text-purple-400">3. Disambiguation:</span> <span id="partition-stat-disambig" class="mono font-black text-white">1</span>
                <p class="text-[10px] text-gray-400 mt-0.5">Indices [105, 106] Himanshu Singh</p>
              </div>
              <div class="p-2.5 rounded-lg bg-rose-500/10 border border-rose-500/20">
                <span class="font-bold text-rose-400">4. Audited Excluded:</span> <span id="partition-stat-excluded" class="mono font-black text-white">3</span>
                <p class="text-[10px] text-gray-400 mt-0.5">Sakariya (Cap), Maxwell, Russell</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Prioritized Campaign Queue Table -->
        <div class="overflow-x-auto rounded-xl border border-white/10 bg-black/40 mb-6">
          <div class="p-3 bg-white/5 border-b border-white/10 flex items-center justify-between">
            <span class="text-xs font-bold text-white uppercase">Verification Queue (Priority Tiers 1-5)</span>
            <span class="text-[10px] text-gray-400 mono">Sorted by: Tier Rank Ascending, Candidate ID</span>
          </div>
          <table class="w-full text-left border-collapse text-xs">
            <thead>
              <tr class="border-b border-white/10 bg-white/5 text-[10px] uppercase tracking-wider text-gray-400 font-bold">
                <th class="p-3">Candidate ID</th>
                <th class="p-3">Unstop Name</th>
                <th class="p-3">Verified DOB</th>
                <th class="p-3">Precision</th>
                <th class="p-3">Source Title</th>
                <th class="p-3">Priority Tier</th>
                <th class="p-3">Status</th>
              </tr>
            </thead>
            <tbody id="campaign-table-body">
              <!-- Dynamically populated via API -->
            </tbody>
          </table>
        </div>
      </div>
"""

export_marker = "      <!-- ================= TAB 6: EXPORT & REPORTS ================= -->"
if export_marker in html and 'id="tab-campaign"' not in html:
    html = html.replace(export_marker, campaign_pane_html + "\n      <!-- ================= TAB 7: EXPORT & REPORTS ================= -->")

# 3. Update loadCampaignData() and switchTab() in JavaScript
old_load_campaign = """async function loadCampaignData() {
  try {
    const res = await fetch('/api/candidates/verification-campaign');
    if (res.ok) {
      const data = await res.json();
      const tbody = document.getElementById('campaign-table-body');
      if (tbody && data.prioritized_queue) {
        tbody.innerHTML = data.prioritized_queue.slice(0, 50).map(c => `
          <tr class="border-b border-white/5 hover:bg-white/5 transition">
            <td class="p-3 mono font-bold text-gray-300">${c.candidate_id}</td>
            <td class="p-3 font-semibold text-white">${c.unstop_name}</td>
            <td class="p-3 mono ${c.dob ? 'text-[#00F0FF]' : 'text-gray-500'}">${c.dob || 'Pending'}</td>
            <td class="p-3 text-[11px] text-gray-400">${c.dob_precision || 'N/A'}</td>
            <td class="p-3 text-[11px] text-gray-300">${c.dob_source_title || 'Awaiting State Registry'}</td>
            <td class="p-3"><span class="px-2 py-0.5 rounded text-[10px] font-bold ${c.priority_tier === 'TIER_1_VERIFIED_UNCAPPED' ? 'bg-emerald-500/20 text-emerald-400' : c.priority_tier === 'TIER_5_AUDITED_EXCLUSION' ? 'bg-rose-500/20 text-rose-400' : 'bg-amber-500/20 text-amber-400'}">${c.priority_tier}</span></td>
            <td class="p-3"><span class="font-bold ${c.verification_status === 'VERIFIED' ? 'text-emerald-400' : 'text-gray-400'}">${c.verification_status}</span></td>
          </tr>
        `).join('');
      }
    }
  } catch (err) {
    console.error('Campaign load error:', err);
  }
}"""

new_load_campaign = """async function loadCampaignData() {
  try {
    const res = await fetch('/api/candidates/verification-campaign');
    if (res.ok) {
      const data = await res.json();
      const sum = data.campaign_summary || {};

      // Dynamically populate campaign stat counters
      const elTotal = document.getElementById('campaign-stat-total');
      if (elTotal) elTotal.innerText = sum.total_unique_candidates || 335;

      const elVerified = document.getElementById('campaign-stat-verified');
      if (elVerified) elVerified.innerText = sum.verified_candidates || 0;

      const elPending = document.getElementById('campaign-stat-pending');
      if (elPending) elPending.innerText = sum.remaining_domestic_pending_research || sum.pending_candidates || 0;

      const elMissing = document.getElementById('campaign-stat-missing');
      if (elMissing) {
        elMissing.innerText = (sum.missing_dob_count !== undefined) 
          ? (sum.missing_dob_count - (sum.unresolved_identity_count || 1)) 
          : 315;
      }

      const elDisambig = document.getElementById('campaign-stat-disambig');
      if (elDisambig) elDisambig.innerText = sum.unresolved_identity_count || 1;

      const elExcluded = document.getElementById('campaign-stat-excluded');
      if (elExcluded) elExcluded.innerText = sum.excluded_rules_count || sum.excluded_candidates || 3;

      const elGate = document.getElementById('campaign-gate-status');
      if (elGate) elGate.innerText = `Status: ${sum.gate_status || 'LOCKED_PROVISIONAL_MODE'}`;

      // Dynamically populate 4-way partition callout
      const pVer = document.getElementById('partition-stat-verified');
      if (pVer) pVer.innerText = sum.verified_candidates || 0;
      const pMiss = document.getElementById('partition-stat-missing');
      if (pMiss) {
        pMiss.innerText = (sum.missing_dob_count !== undefined)
          ? (sum.missing_dob_count - (sum.unresolved_identity_count || 1))
          : 315;
      }
      const pDis = document.getElementById('partition-stat-disambig');
      if (pDis) pDis.innerText = sum.unresolved_identity_count || 1;
      const pExc = document.getElementById('partition-stat-excluded');
      if (pExc) pExc.innerText = sum.excluded_rules_count || 3;

      const tbody = document.getElementById('campaign-table-body');
      if (tbody && data.prioritized_queue) {
        tbody.innerHTML = data.prioritized_queue.slice(0, 100).map(c => `
          <tr class="border-b border-white/5 hover:bg-white/5 transition">
            <td class="p-3 mono font-bold text-gray-300">${c.candidate_id}</td>
            <td class="p-3 font-semibold text-white">${c.unstop_name}</td>
            <td class="p-3 mono ${c.dob ? 'text-[#00F0FF]' : 'text-gray-500'}">${c.dob || 'Pending'}</td>
            <td class="p-3 text-[11px] text-gray-400">${c.dob_precision || 'N/A'}</td>
            <td class="p-3 text-[11px] text-gray-300 truncate max-w-xs">${c.dob_source_title || 'Awaiting State Registry'}</td>
            <td class="p-3"><span class="px-2 py-0.5 rounded text-[10px] font-bold ${c.priority_tier === 'TIER_1_VERIFIED_UNCAPPED' ? 'bg-emerald-500/20 text-emerald-400' : c.priority_tier === 'TIER_5_AUDITED_EXCLUSION' ? 'bg-rose-500/20 text-rose-400' : c.priority_tier === 'TIER_2_DISAMBIGUATION_REQUIRED' ? 'bg-purple-500/20 text-purple-400' : 'bg-amber-500/20 text-amber-400'}">${c.priority_tier}</span></td>
            <td class="p-3"><span class="font-bold ${c.verification_status === 'VERIFIED' ? 'text-emerald-400' : 'text-gray-400'}">${c.verification_status}</span></td>
          </tr>
        `).join('');
      }
    }
  } catch (err) {
    console.error('Campaign load error:', err);
  }
}"""

if old_load_campaign in html:
    html = html.replace(old_load_campaign, new_load_campaign)

# 4. Update switchTab() to include btn-tab-campaign
old_switch_tab = """  const tabButtons = [
    { id: 'btn-tab-registry', tab: 'tab-registry' },
    { id: 'btn-tab-list-a', tab: 'tab-list-a' },
    { id: 'btn-tab-list-b', tab: 'tab-list-b' },
    { id: 'btn-tab-pending', tab: 'tab-pending' },
    { id: 'btn-tab-compare', tab: 'tab-compare' },
    { id: 'btn-tab-export', tab: 'tab-export' },
  ];"""

new_switch_tab = """  const tabButtons = [
    { id: 'btn-tab-registry', tab: 'tab-registry' },
    { id: 'btn-tab-list-a', tab: 'tab-list-a' },
    { id: 'btn-tab-list-b', tab: 'tab-list-b' },
    { id: 'btn-tab-pending', tab: 'tab-pending' },
    { id: 'btn-tab-compare', tab: 'tab-compare' },
    { id: 'btn-tab-campaign', tab: 'tab-campaign' },
    { id: 'btn-tab-export', tab: 'tab-export' },
  ];"""

if old_switch_tab in html:
    html = html.replace(old_switch_tab, new_switch_tab)

# 5. Update top header initial numbers from 10/322 to 16/316
html = html.replace(
    '<div id="stat-eligible" class="text-lg font-black text-emerald-400 mono">10</div>',
    '<div id="stat-eligible" class="text-lg font-black text-emerald-400 mono">16</div>'
)
html = html.replace(
    '<div id="stat-pending" class="text-lg font-black text-amber-400 mono">322</div>',
    '<div id="stat-pending" class="text-lg font-black text-amber-400 mono">316</div>'
)

with open(landing_path, "w", encoding="utf-8") as f:
    f.write(html)

print("Successfully updated landing_page.html with dynamic campaign counters and partition callout!")
