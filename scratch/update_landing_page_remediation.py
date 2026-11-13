"""
Script to update landing_page.html for Round 1 Data Completeness Remediation:
1. Replaces 'Top 10 Absolute Youngest' title with 'Provisional Youngest Verified Candidates'
2. Injects prominent amber methodology limitation warning banner
3. Corrects uncapped terminology to 'Senior International Appearance Audit'
4. Adds DOB Campaign tab and prioritized queue view
5. Updates client-side JavaScript to fetch and display campaign data
"""

from pathlib import Path

landing_path = Path("landing_page.html")
with open(landing_path, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Replace List A Title
html = html.replace(
    "List A: Top 10 Absolute Youngest Verified Uncapped Stars",
    "List A: Provisional Youngest Verified Candidates"
)

# 2. Add limitation banner above List A cards
old_list_a_header = '<div id="tab-list-a" class="tab-pane hidden">'
new_list_a_banner = '''<div id="tab-list-a" class="tab-pane hidden">
        <!-- Prominent Methodology Limitation Banner -->
        <div class="bg-amber-500/10 border-2 border-amber-500/50 rounded-2xl p-4 mb-6 flex items-start gap-3 shadow-lg">
          <span class="text-2xl mt-0.5">⚠️</span>
          <div>
            <div class="text-xs font-black uppercase tracking-wider text-amber-400">Research Completeness & Methodology Limitation</div>
            <p class="text-xs text-gray-300 mt-1 leading-relaxed">
              <strong>METHODOLOGY LIMITATION:</strong> This list represents the youngest candidates among those verified to date (10 of 335 candidates). 322 candidates in the Unstop candidate pool remain in the verification queue awaiting primary source DOB and Senior International Appearance Audits. Because unverified candidates could be younger than those listed here, this ranking is <strong>PROVISIONAL</strong> and strictly for internal research. The designation <em>'Top 10 Absolute Youngest'</em> is locked until 100% of potentially eligible candidates have completed verification.
            </p>
          </div>
        </div>'''
if old_list_a_header in html:
    html = html.replace(old_list_a_header, new_list_a_banner)

# 3. Replace closed-world BCCI references
html = html.replace("closed-world BCCI cap verification", "Senior International Appearance Audit")
html = html.replace("closed-world BCCI cap registry", "Senior International Appearance Audit")
html = html.replace("closed-world BCCI", "Senior International Appearance Audit")
html = html.replace(
    "Negative senior cap verified against BCCI Senior Cap Register (Tests 1–314, ODIs 1–258, T20Is 1–120). Zero synthetic performance metrics or role quotas applied.",
    "Conclusively verified uncapped under Senior International Appearance Audit (0 Tests, 0 ODIs, 0 T20Is). Zero synthetic performance metrics or speculative valuations applied."
)

# 4. Remove unsupported speed
html = html.replace("140+ km/h Indian pace depth", "Indian pace depth")

# 5. Add Campaign Tab Button in Navigation
tab_needle = '''        <button onclick="switchTab('tab-export')" id="btn-tab-export" class="px-4 py-2 rounded-xl bg-white/5 hover:bg-white/10 text-[#EDAA16] border border-[#EDAA16]/30 transition">
          📥 Export & Reports
        </button>'''
new_tabs = '''        <button onclick="switchTab('tab-campaign')" id="btn-tab-campaign" class="px-4 py-2 rounded-xl bg-white/5 hover:bg-white/10 text-cyan-400 border border-cyan-500/30 transition">
          🔍 DOB Campaign (335)
        </button>
''' + tab_needle
if tab_needle in html:
    html = html.replace(tab_needle, new_tabs)

# 6. Add Campaign Tab Pane before tab-export
export_pane_needle = '<!-- ================= TAB 5: COMPARE ================= -->'
campaign_pane = '''<!-- ================= TAB 6: DOB VERIFICATION CAMPAIGN ================= -->
      <div id="tab-campaign" class="tab-pane hidden">
        <div class="bg-gradient-to-r from-cyan-950/40 via-black to-black border border-cyan-500/30 rounded-2xl p-6 mb-6">
          <div class="flex items-start justify-between flex-wrap gap-4 mb-4">
            <div>
              <span class="px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase tracking-widest bg-cyan-500 text-black shadow-sm">RESEARCH COMPLETENESS GATE</span>
              <h3 class="text-xl font-black text-white uppercase mt-1">DOB Verification Campaign & Pool Coverage</h3>
              <p class="text-xs text-gray-300 mt-1 max-w-2xl">
                Protocol v1.2 audit coverage across all 335 candidate records. Tracks full DOB precision, source URLs, and Senior International Appearance Audits. Zero synthetic dates or simulated statistics.
              </p>
            </div>
            <span class="px-3 py-1 rounded-full bg-amber-500/20 border border-amber-500 text-amber-400 text-xs font-bold mono">
              Status: LOCKED_PROVISIONAL_MODE
            </span>
          </div>

          <!-- Campaign Counters -->
          <div class="grid grid-cols-2 sm:grid-cols-6 gap-3 pt-4 border-t border-white/10 text-center">
            <div class="bg-black/50 p-2.5 rounded-xl border border-white/10">
              <div class="text-[10px] text-gray-400 font-bold uppercase">Total Unique</div>
              <div class="text-base font-black text-white mono">335</div>
            </div>
            <div class="bg-black/50 p-2.5 rounded-xl border border-emerald-500/30">
              <div class="text-[10px] text-emerald-400 font-bold uppercase">Verified Full DOB</div>
              <div class="text-base font-black text-emerald-400 mono">10</div>
            </div>
            <div class="bg-black/50 p-2.5 rounded-xl border border-amber-500/30">
              <div class="text-[10px] text-amber-400 font-bold uppercase">Missing DOB</div>
              <div class="text-base font-black text-amber-400 mono">322</div>
            </div>
            <div class="bg-black/50 p-2.5 rounded-xl border border-purple-500/30">
              <div class="text-[10px] text-purple-400 font-bold uppercase">Year-Only DOB</div>
              <div class="text-base font-black text-purple-400 mono">0</div>
            </div>
            <div class="bg-black/50 p-2.5 rounded-xl border border-rose-500/30">
              <div class="text-[10px] text-rose-400 font-bold uppercase">Capped/Overseas</div>
              <div class="text-base font-black text-rose-400 mono">3</div>
            </div>
            <div class="bg-black/50 p-2.5 rounded-xl border border-cyan-500/30">
              <div class="text-[10px] text-cyan-400 font-bold uppercase">Pending Research</div>
              <div class="text-base font-black text-cyan-400 mono">322</div>
            </div>
          </div>
        </div>

        <!-- Campaign Table -->
        <div class="overflow-x-auto rounded-xl border border-white/10 bg-black/40 mb-6">
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

      ''' + export_pane_needle
if export_pane_needle in html:
    html = html.replace(export_pane_needle, campaign_pane)

# 7. Add JS to render campaign table
old_init = "async function initPhase1() {"
new_init = '''async function loadCampaignData() {
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
}

async function initPhase1() {
  loadCampaignData();'''
if old_init in html:
    html = html.replace(old_init, new_init)

with open(landing_path, "w", encoding="utf-8") as f:
    f.write(html)

print("Successfully updated landing_page.html with Research Completeness Gate & Campaign Tab!")
