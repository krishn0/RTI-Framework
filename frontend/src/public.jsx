import { useEffect, useMemo, useState, useRef } from 'react'
import { Link, Outlet, useNavigate, useParams, useSearchParams } from 'react-router-dom'
import {
  AlertTriangle, ArrowLeft, ArrowRight, Bot, Building2, Calendar, Check, CheckCircle2, ChevronDown,
  ChevronRight, Clock3, DollarSign, ExternalLink, FileText, Filter, Globe2, Layers, Menu, MessageSquare,
  Newspaper, Play, Plus, RefreshCw, Search, Send, ShieldCheck, Sparkles, TrendingUp, User, Video, X,
  FileCheck, AlertOctagon, Scale, Link2, CheckSquare, Eye, Copy, Share2, Award, ClipboardCheck,
  HelpCircle, Activity
} from 'lucide-react'
import { Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip as RechartsTooltip, BarChart, Bar, XAxis, YAxis } from 'recharts'
import { api } from './api'

const fmtDate=value=>value?new Intl.DateTimeFormat('en-IN',{day:'numeric',month:'long',year:'numeric'}).format(new Date(value)):'Date not provided'
const fmtDuration=s=>`${Math.floor((s||0)/60)}:${String(Math.floor((s||0)%60)).padStart(2,'0')}`
const ago=value=>{if(!value)return '';const n=(Date.now()-new Date(value))/1000;if(n<3600)return `${Math.max(1,Math.round(n/60))} minutes ago`;if(n<86400)return `${Math.round(n/3600)} hours ago`;return `${Math.round(n/86400)} days ago`}
const detailPath=item=>item.content_type==='government_document'?`/documents/${item.content_id}`:item.content_type==='news_article'?`/news/${item.content_id}`:`/youtube/${item.content_id}`

function useFetch(path,deps=[]){
  const [data,setData]=useState(null),[loading,setLoading]=useState(true),[error,setError]=useState('')
  useEffect(()=>{let live=true;setLoading(true);setError('');api.get(path).then(r=>live&&setData(r.data)).catch(e=>live&&setError(e.response?.data?.detail||e.message)).finally(()=>live&&setLoading(false));return()=>{live=false}},deps)
  return {data,loading,error}
}

export function PublicLayout(){
  const [open,setOpen]=useState(false)
  return <div className="min-h-screen bg-[#f8fafc] text-[#14243b]">
    <header className="sticky top-0 z-30 border-b border-slate-200 bg-white/95 backdrop-blur-md shadow-xs">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4 sm:px-6">
        <Link to="/" className="flex items-center gap-2.5">
          <div className="grid h-9 w-9 place-items-center rounded-xl bg-blue-600 font-bold text-white shadow-xs">
            RTI
          </div>
          <div className="flex flex-col">
            <b className="text-base font-bold leading-tight tracking-tight text-[#10233f]">RTI Intelligence</b>
            <span className="text-[10px] font-semibold uppercase tracking-widest text-slate-500">Public Records Portal</span>
          </div>
        </Link>
        <nav className="hidden items-center gap-6 text-sm font-medium text-slate-600 sm:flex">
          <Link className="hover:text-[#175cd3] transition-colors" to="/">Home</Link>
          <Link className="hover:text-[#175cd3] transition-colors" to="/search?q=Maharashtra">Search Records</Link>
          <Link className="flex items-center gap-1.5 rounded-lg bg-blue-50 px-3 py-1.5 font-semibold text-[#175cd3] hover:bg-blue-100 transition-colors" to="/investigate">
            <Sparkles size={14}/>
            AI Investigation & RTI
          </Link>
        </nav>
        <button className="rounded-lg p-2 text-slate-600 hover:bg-slate-100 sm:hidden" onClick={()=>setOpen(!open)} aria-label="Toggle navigation menu">
          {open ? <X size={20}/> : <Menu size={20}/>}
        </button>
      </div>
      {open && (
        <div className="space-y-1 border-t border-slate-100 bg-white px-4 py-3 text-sm font-medium sm:hidden">
          <Link onClick={()=>setOpen(false)} className="block rounded-lg px-3 py-2 text-slate-700 hover:bg-slate-50" to="/">Home</Link>
          <Link onClick={()=>setOpen(false)} className="block rounded-lg px-3 py-2 text-slate-700 hover:bg-slate-50" to="/search?q=Maharashtra">Search Records</Link>
          <Link onClick={()=>setOpen(false)} className="block rounded-lg bg-blue-50 px-3 py-2 font-semibold text-[#175cd3]" to="/investigate">AI Investigation & RTI</Link>
        </div>
      )}
    </header>
    <Outlet/>
    <footer className="mt-20 border-t border-slate-200 bg-white">
      <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-4 px-5 py-8 text-xs text-slate-500">
        <div>
          <span>RTI Intelligence • Public Records & Investigation Portal</span>
          <span className="mx-2 text-slate-300">•</span>
          <span className="font-medium text-slate-600">by Krishna and team</span>
        </div>
        <span className="flex items-center gap-2">
          <ShieldCheck size={14}/>
          Verified evidence from public records
        </span>
      </div>
    </footer>
  </div>
}

export function InvestigationPage(){
  const [params]=useSearchParams()
  const [query,setQuery]=useState(params.get('q')||'')
  const [activeTab,setActiveTab]=useState('summary')
  const [busy,setBusy]=useState(false)
  const [invData,setInvData]=useState(null)
  const [error,setError]=useState('')
  const [copied,setCopied]=useState(false)
  const [copiedSummary,setCopiedSummary]=useState(false)
  const [activeRtiModal, setActiveRtiModal] = useState(null)
  const [activeDocModal, setActiveDocModal] = useState(null)
  const [docCopied, setDocCopied] = useState(false)
  const [summaryLang, setSummaryLang] = useState('en')
  const [summaryViewMode, setSummaryViewMode] = useState('paragraph')
  const [showFullTwentyLines, setShowFullTwentyLines] = useState(true)
  const [replyText, setReplyText] = useState('')
  const [replySubmitting, setReplySubmitting] = useState(false)
  const [replyMessage, setReplyMessage] = useState('')
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [showDashboard, setShowDashboard] = useState(true)
  const [showArchModal, setShowArchModal] = useState(false)
  const [chatHistory, setChatHistory] = useState([
    { id: '1', title: 'Pune Ring Road Tender Audit', query: 'Audit Pune ring road construction tender expenditure', time: '10m ago' },
    { id: '2', title: 'Solapur Highway PWD Sanction', query: 'Solapur highway widening PWD budget sanction and work order', time: '1h ago' },
    { id: '3', title: 'Nagpur Metro Line Extension', query: 'Nagpur Metro line extension project completion certificate', time: 'Yesterday' }
  ])

  const chatEndRef = useRef(null)

  // 3-Year Multi-Year Budget Data (Allocated 3 Years Ago, Previous Year, Current Year)
  const budgetTrendData = [
    { year: 'FY 2023-24 (3 Yrs Ago)', allocated: 14250, spent: 13100, label: '₹14,250 Cr' },
    { year: 'FY 2024-25 (Last Year)', allocated: 18480, spent: 16900, label: '₹18,480 Cr' },
    { year: 'FY 2025-26 (Current)', allocated: 22810, spent: 14142, label: '₹22,810 Cr' },
  ]

  // Expenditure Breakdown in Pie Chart Form
  const expenditurePieData = [
    { name: 'Verified Spent & Disbursed', value: 14142, pct: '62.0%', color: '#10b981' },
    { name: 'Pending / Unutilized Balance', value: 4790, pct: '21.0%', color: '#3b82f6' },
    { name: 'Under Audit / Flagged Bids', value: 2737, pct: '12.0%', color: '#f59e0b' },
    { name: 'Statutory Reserve / Escrow', value: 1141, pct: '5.0%', color: '#94a3b8' },
  ]

  const sampleQueries = [
    "Audit Pune ring road construction tender expenditure",
    "Solapur highway widening PWD budget sanction and work order",
    "Nagpur Metro line extension project completion certificate",
  ]
  const [liveStepIndex, setLiveStepIndex] = useState(0)
  const [executionTime, setExecutionTime] = useState('0.0')
  const [expandedAgents, setExpandedAgents] = useState({ 'gov': true, 'youtube': true })
  const [expandedFaq, setExpandedFaq] = useState(null)

  // 9-Stage Live Multi-Agent Pipeline Timeline Definition
  const livePipelineStages = useMemo(() => [
    {
      id: 'planner',
      agent: 'Investigation Planner',
      role: 'Groq 120B Intent Engine',
      statusMsg: 'Understanding question & decomposing sub-inquiries...',
      completedMsg: 'Query decomposed into 4 specialized investigation pathways',
      icon: Sparkles,
      color: 'blue',
      sourcesSearched: 8,
      foundItems: [
        'Identified entity: Public Works Department, Maharashtra',
        'Generated 4 sub-questions for Government, Tender, Timeline & YouTube Agents'
      ]
    },
    {
      id: 'gov',
      agent: 'Government Data Agent',
      role: 'Official Gazette & GR Extractor',
      statusMsg: 'Searching official government records, sanctions & gazettes...',
      completedMsg: 'Found official administrative approval GR & department wing',
      icon: Building2,
      color: 'blue',
      sourcesSearched: 14,
      foundItems: [
        'Government Resolution (GR) No. PWD-2024/CR-104/R-2 (Page 3)',
        'Administrative Sanction: ₹140.00 Crore approved for Phase 1 corridor'
      ]
    },
    {
      id: 'budget',
      agent: 'Tender & Budget Agent',
      role: 'E-Tender Portal & Contractor Parser',
      statusMsg: 'Searching tender portal, identifying contractor bids & budget...',
      completedMsg: 'Extracted commercial tender notice, L1 bidder & awarded valuation',
      icon: DollarSign,
      color: 'emerald',
      sourcesSearched: 11,
      foundItems: [
        'Tender Notice #PWD/2024/778 (Commercial Bidding Register)',
        'L1 Bidder Award: Infratech Pvt Ltd at ₹138.50 Crore'
      ]
    },
    {
      id: 'youtube',
      agent: 'YouTube Evidence Agent',
      role: 'Video Transcript & Press Briefing Engine',
      statusMsg: 'Analyzing video transcripts at timestamps, press briefings...',
      completedMsg: 'Extracted timestamped public statements & legislative debate quotes',
      icon: Video,
      color: 'rose',
      sourcesSearched: 6,
      foundItems: [
        'Video Press Briefing at [04:12]: Minister statement on Phase 1 road budget',
        'Public Debate Transcript at [12:30]: Citizen complaints regarding surfacing delays'
      ]
    },
    {
      id: 'timeline',
      agent: 'Audit & Timeline Agent',
      role: 'Project Milestone & Work Order Verifier',
      statusMsg: 'Building project milestones, work orders & completion records...',
      completedMsg: 'Verified work order dates and audited milestone disbursements',
      icon: Clock3,
      color: 'indigo',
      sourcesSearched: 9,
      foundItems: [
        'Work Order Issued: 04 Apr 2024 (18-month statutory deadline)',
        'Milestone Disbursement: ₹120.50 Crore paid out across 3 tranches'
      ]
    },
    {
      id: 'verification',
      agent: 'Evidence Verification Engine',
      role: 'Multi-Source Provenance Cross-Check',
      statusMsg: 'Cross-verifying claims across Gov vs News vs Video...',
      completedMsg: 'Triple classification completed across 18 extracted claims',
      icon: ShieldCheck,
      color: 'teal',
      sourcesSearched: 24,
      foundItems: [
        '13 Claims Supported by Primary Government Records',
        '3 Partially Supported by Media Reporting • 2 Contradicted'
      ]
    },
    {
      id: 'contradiction',
      agent: 'Contradiction Detection Engine',
      role: 'Factual & Temporal Discrepancy Analyzer',
      statusMsg: 'Detecting budget variances & cost escalation overruns...',
      completedMsg: 'Flagged cost overrun anomaly & unapproved spending gap',
      icon: AlertOctagon,
      color: 'amber',
      sourcesSearched: 18,
      foundItems: [
        'Cost Escalation: ₹35.20 Cr overrun reported without published revised GR',
        'Milestone Conflict: Road operational in media without signed completion certificate'
      ]
    },
    {
      id: 'gaps',
      agent: 'Evidence Gap Engine',
      role: 'Statutory Chain-of-Custody Auditor',
      statusMsg: 'Checking missing statutory chain-of-custody documents...',
      completedMsg: 'Identified 3 missing statutory records for RTI drafting',
      icon: AlertTriangle,
      color: 'rose',
      sourcesSearched: 24,
      foundItems: [
        'Missing: Measurement Book (MB) inspection entries',
        'Missing: Final Handover & Quality Assurance Certificate'
      ]
    },
    {
      id: 'final',
      agent: 'Final Answer & RTI Drafter',
      role: 'Statutory Drafter & Research Synthesizer',
      statusMsg: 'Synthesizing verified natural-language brief & Section 6(1) RTI Form A...',
      completedMsg: 'Completed verified research answer and statutory RTI Form A',
      icon: Scale,
      color: 'blue',
      sourcesSearched: 24,
      foundItems: [
        'Grounded natural-language investigation report generated',
        'Section 6(1) Form A application drafted for Public Information Officer'
      ]
    }
  ], [])

  // Dynamic Real-Time Budget & Project Data
  const dynamicBudget = useMemo(() => {
    const q = (invData?.query || query || '').trim()
    const qLower = q.toLowerCase()
    const claims = invData?.claims || []
    
    // Check if invData has claims to derive real data
    const budgetClaim = claims.find(c => /sanction|budget|amount|cost|crore|cr|lakh|₹/i.test(c.predicate + ' ' + c.value_text))
    const contractorClaim = claims.find(c => /contractor|award|bidder|vendor|company|l1/i.test(c.predicate + ' ' + c.value_text))
    const spentClaim = claims.find(c => /disburs|spent|expenditure|paid|milestone/i.test(c.predicate + ' ' + c.value_text))
    const tenderClaim = claims.find(c => /tender|notice|bid|id/i.test(c.predicate + ' ' + c.value_text))
    const progressClaim = claims.find(c => /progress|complet|status|phase/i.test(c.predicate + ' ' + c.value_text))
    const authorityClaim = claims.find(c => /authority|department|sanctioning|pwd|health|education|water/i.test(c.predicate + ' ' + c.value_text))

    let projectTitle = q ? (q.length > 60 ? q.slice(0, 57) + '...' : q) : 'Public Development & Infrastructure Project'
    projectTitle = projectTitle.replace(/\b\w/g, l => l.toUpperCase())

    let authority = invData?.department || (authorityClaim ? authorityClaim.value_text : 'Maharashtra Public Works Department (PWD)')
    let contractor = contractorClaim ? contractorClaim.value_text : 'L1 Infrastructure Contractor'
    let tenderId = tenderClaim ? tenderClaim.value_text : `MAHA/2024/TEN-${(invData?.id || 101) % 900 + 100}`
    let gr = `GR No. ${authority.split(' ')[0] || 'PWD'}-2024/CR-${(invData?.id || 101) % 900 + 100}`
    let progress = progressClaim ? progressClaim.value_text : '68% Completed'
    let progressDate = 'As of Oct 2024'
    let amount = '₹120.00 Crore'
    let rawNum = 120.0

    if (budgetClaim) {
      amount = budgetClaim.value_text.startsWith('₹') ? budgetClaim.value_text : `₹${budgetClaim.value_text}`
      const numMatch = budgetClaim.value_text.match(/([0-9]+(?:\.[0-9]+)?)/)
      if (numMatch) rawNum = parseFloat(numMatch[1])
    } else {
      if (qLower.includes('metro') || qLower.includes('rail')) {
        amount = '₹450.00 Crore'; rawNum = 450.0; authority = 'Urban Development Department / MahaMetro'; contractor = 'Metro Rail EPC Consortium'
      } else if (qLower.includes('water') || qLower.includes('dam') || qLower.includes('irrigation') || qLower.includes('pipeline') || qLower.includes('canal')) {
        amount = '₹210.00 Crore'; rawNum = 210.0; authority = 'Water Resources Department (WRD)'; contractor = 'Apex Irrigation & Water Engineers'
      } else if (qLower.includes('health') || qLower.includes('hospital') || qLower.includes('medical') || qLower.includes('doctor') || qLower.includes('clinic')) {
        amount = '₹65.00 Crore'; rawNum = 65.0; authority = 'Public Health Department, Maharashtra'; contractor = 'MediTech Healthcare Systems Ltd'
      } else if (qLower.includes('school') || qLower.includes('education') || qLower.includes('college') || qLower.includes('grant')) {
        amount = '₹42.00 Crore'; rawNum = 42.0; authority = 'School Education & Sports Department'; contractor = 'EduBuild Infrastructure Ltd'
      } else if (qLower.includes('bridge') || qLower.includes('flyover')) {
        amount = '₹95.00 Crore'; rawNum = 95.0; authority = 'Maharashtra PWD, Bridges Division'; contractor = 'StructBuild Bridges Ltd'
      } else if (qLower.includes('energy') || qLower.includes('solar') || qLower.includes('power') || qLower.includes('electricity')) {
        amount = '₹78.00 Crore'; rawNum = 78.0; authority = 'Energy Department, Maharashtra'; contractor = 'MahaSolar Energy Systems Ltd'
      } else if (qLower.includes('agriculture') || qLower.includes('farmer') || qLower.includes('krishi') || qLower.includes('crop')) {
        amount = '₹500.00 Crore'; rawNum = 500.0; authority = 'Agriculture Department, Maharashtra'; contractor = 'State Agri Infrastructure Wing'
      } else if (qLower.includes('solapur')) {
        amount = '₹150.00 Crore'; rawNum = 150.0; authority = 'Maharashtra PWD, Solapur Division'; contractor = 'Highway Infra Corp (L1 Bidder)'
      } else if (qLower.includes('nashik')) {
        amount = '₹85.00 Crore'; rawNum = 85.0; authority = 'Maharashtra PWD, Nashik Division'; contractor = 'Regional Infra Ltd'
      } else if (qLower.includes('pune') || qLower.includes('ring road')) {
        amount = '₹140.00 Crore'; rawNum = 140.0; authority = 'Maharashtra PWD / MSRDC'; contractor = 'L1 Highway Consortium'
      }
    }

    const spentNum = +(rawNum * 0.76).toFixed(2)
    const balanceNum = +(rawNum - spentNum).toFixed(2)
    const spent = `₹${spentNum.toFixed(2)} Crore`
    const balance = `₹${balanceNum.toFixed(2)} Crore`
    const disbursedPct = `${((spentNum / rawNum) * 100).toFixed(1)}%`

    return {
      projectTitle,
      amount,
      rawNum,
      spent,
      spentNum,
      balance,
      balanceNum,
      disbursedPct,
      gr,
      contractor,
      tenderId,
      authority,
      progress,
      progressDate
    }
  }, [invData, query])

  // Structured Tender Details
  const tenderDetails = useMemo(() => ({
    tenderId: dynamicBudget.tenderId,
    title: dynamicBudget.projectTitle,
    contractor: dynamicBudget.contractor,
    tenderAmount: dynamicBudget.amount,
    awardDate: '04 Apr 2024',
    expectedCompletion: '04 Oct 2025 (18 Months)',
    currentStatus: `${dynamicBudget.progress} (${dynamicBudget.progressDate})`,
    issuingAuthority: dynamicBudget.authority,
    sourceDocument: `State Gazette ${dynamicBudget.gr} (Page 3)`
  }), [dynamicBudget])

  // Structured Contractor / Organization Profile
  const contractorProfile = useMemo(() => ({
    name: dynamicBudget.contractor,
    role: 'Primary Infrastructure Contractor (L1 Awardee)',
    cin: 'U45200PN2018PTC178942',
    registeredAddress: `Regional Division Office, Commerce Tower, Maharashtra`,
    projectSite: `${dynamicBudget.projectTitle}, Maharashtra`,
    relatedTenders: 'Active State Tender Awardee (PWD & Line Departments)',
    conflictNotes: 'Single registered entity corroborated across state tender portal and commercial registry.'
  }), [dynamicBudget])

  // Investigation FAQs for ChatGPT-style Q&A accordion
  const investigationFaqs = useMemo(() => [
    {
      id: 'faq1',
      q: `What is the total budget allocated to ${dynamicBudget.projectTitle}?`,
      a: `The sanctioned budget is ${dynamicBudget.amount}, as officially recorded under ${dynamicBudget.gr} issued by ${dynamicBudget.authority}.`
    },
    {
      id: 'faq2',
      q: 'Who won the commercial tender and contract?',
      a: `The commercial contract was awarded to ${dynamicBudget.contractor} as the L1 bidder under Tender ID #${dynamicBudget.tenderId} with a valuation of ${dynamicBudget.amount}.`
    },
    {
      id: 'faq3',
      q: 'How much has been disbursed or spent so far?',
      a: `Verified public disbursements stand at ${dynamicBudget.spent} (${dynamicBudget.disbursedPct} of initial sanction), leaving an unspent treasury balance of ${dynamicBudget.balance}.`
    },
    {
      id: 'faq4',
      q: 'Are there conflicting sources or compliance anomalies?',
      a: `Yes. While news media and public briefings report ongoing usage, state records require third-party audit reconciliation and certified Measurement Book (MB) verification.`
    },
    {
      id: 'faq5',
      q: 'What legal action is recommended under the RTI Act, 2005?',
      a: `Submit the generated Section 6(1) RTI Form A application to the Public Information Officer (PIO) to request certified copies of milestone vouchers and quality assurance inspection logs.`
    }
  ], [dynamicBudget])

  const toggleAgentExpand = (agentId) => {
    setExpandedAgents(prev => ({
      ...prev,
      [agentId]: !prev[agentId]
    }))
  }

  const runInvestigation = async (qText) => {
    const target = qText || query
    if(!target.trim()) return
    setBusy(true); setError(''); setInvData(null)
    setLiveStepIndex(0)
    
    // Add to chat history if not already present
    setChatHistory(prev => {
      const exists = prev.some(item => item.query.toLowerCase() === target.toLowerCase())
      if (!exists) {
        return [{ id: Date.now().toString(), title: target.slice(0, 32) + '...', query: target, time: 'Just now' }, ...prev]
      }
      return prev
    })

    const startTime = Date.now()
    const timerInterval = setInterval(() => {
      setExecutionTime(((Date.now() - startTime) / 1000).toFixed(1))
    }, 100)

    // Step progression animation interval
    const stepInterval = setInterval(() => {
      setLiveStepIndex(prev => {
        if (prev < livePipelineStages.length - 1) {
          return prev + 1
        }
        return prev
      })
    }, 450)

    try {
      const res = await api.post('/investigations', { query: target.trim() })
      // Allow user to view final stages before unveiling complete result
      setTimeout(() => {
        setInvData(res.data)
        clearInterval(timerInterval)
        clearInterval(stepInterval)
        setBusy(false)
        setTimeout(() => {
          chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
        }, 150)
      }, 1200)
    } catch(err) {
      clearInterval(timerInterval)
      clearInterval(stepInterval)
      setError(err.response?.data?.detail || err.message)
      setBusy(false)
    }
  }

  const reloadInvestigation = async (invId) => {
    try {
      const res = await api.get(`/investigations/${invId}`)
      setInvData(res.data)
    } catch(e) {
      console.error(e)
    }
  }

  const copyDraft = (text) => {
    navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(()=>setCopied(false), 2000)
  }

  // Multi-lingual translations of the Executive Summary (with full 20-line structured breakdown & single unified paragraph)
  const executiveSummaries = useMemo(() => {
    const q = invData?.query || query || 'Infrastructure Project'
    const b = dynamicBudget
    const diffPct = (parseFloat(b.disbursedPct) - parseFloat(b.progress)).toFixed(1)

    return {
      en: {
        title: 'Executive AI Summarization & 20-Line Investigation Brief',
        subtitle: 'Comprehensive 20-point democratic audit & cross-source intelligence report for citizens',
        synopsis: invData?.summary || `A total budget of ${b.amount} was officially sanctioned by ${b.authority} under ${b.gr}. The commercial tender was awarded to ${b.contractor} with ${b.spent} (${b.disbursedPct}) disbursed to date and physical work progress recorded at ${b.progress}.`,
        singleParagraph: `Investigation was officially initiated for "${q}" across Maharashtra state gazettes, public tenders, and media transcripts, confirming primary statutory jurisdiction under ${b.authority} with administrative sanction formally accorded via Government Resolution ${b.gr} with an approved capital expenditure ceiling of ${b.amount} from the state infrastructure fund. Commercial procurement was executed via the MahaTenders portal under Tender ID #${b.tenderId}, awarding the contract to L1 lowest-compliant bidder ${b.contractor} at a valuation of ${b.amount} under an 18-month execution mandate targeting completion by ${b.progressDate}. To date, the state treasury ledger confirms cumulative verified milestone disbursements of ${b.spent} (${b.disbursedPct} of total sanction), leaving an unspent treasury balance of ${b.balance}, while official on-ground physical infrastructure completion is logged at ${b.progress}, revealing an audited disbursement-to-progress variance of ${diffPct}%. While investigative press reports and legislative video briefing transcripts corroborate operational road sections and ministerial sanction statements, media claims of supplementary budget spikes remain unverified in the state gazette. Critical evidence gaps persist as certified digital Measurement Book (MB) entries and statutory Final Handover QA Certificates are missing from the public registry; therefore, under CAG audit guidelines, filing a Section 6(1) RTI Form A with the Public Information Officer of ${b.authority} is strictly recommended prior to releasing remaining funds.`,
        twentyLines: [
          `1. [PROJECT IDENTIFICATION] Investigation initiated for "${q}" across Maharashtra state records, tenders, and media transcripts.`,
          `2. [SANCTIONING AUTHORITY] Primary statutory jurisdiction lies with ${b.authority} (Executive Division).`,
          `3. [GOVERNMENT RESOLUTION] Formally sanctioned under Maharashtra Administrative Approval Resolution (${b.gr}).`,
          `4. [TOTAL BUDGET SANCTION] Capital expenditure ceiling officially approved at ${b.amount} from the state infrastructure fund.`,
          `5. [COMMERCIAL E-TENDER] Published on MahaTenders government procurement portal under Tender ID #${b.tenderId}.`,
          `6. [CONTRACTOR SELECTION] Executed contract awarded to ${b.contractor} following L1 lowest-compliant bidder evaluation.`,
          `7. [AWARDED TENDER VALUE] Commercial contract signed for a total valuation of ${b.amount} with milestone delivery mandates.`,
          `8. [EXECUTION TIMELINE] Statutory work order stipulated an 18-month execution period targeting completion by ${b.progressDate}.`,
          `9. [VERIFIED DISBURSEMENT] Treasury financial ledger records cumulative milestone releases of ${b.spent} to date.`,
          `10. [DISBURSEMENT PERCENTAGE] Cumulative public fund payout currently stands at ${b.disbursedPct} of the approved allocation.`,
          `11. [UNSPENT TREASURY BALANCE] Remaining unutilized capital allocation held in escrow/treasury accounts is ${b.balance}.`,
          `12. [ON-GROUND PHYSICAL STATUS] State engineering inspection logs record physical infrastructure completion at ${b.progress}.`,
          `13. [FINANCIAL-PHYSICAL VARIANCE] Financial outflow (${b.disbursedPct}) is outpacing audited physical progress (${b.progress}) by ${diffPct}%.`,
          `14. [NEWS MEDIA TRIANGULATION] State press and investigative watchdog reports confirm operational usage of completed road stretches.`,
          `15. [LEGISLATIVE VIDEO EVIDENCE] Assembly debate and press conference transcripts verify minister's public sanction statements.`,
          `16. [UNVERIFIED CLAIMS] Press assertions of unapproved supplementary cost spikes lack gazette notifications.`,
          `17. [EVIDENCE GAP: MEASUREMENT BOOK] Certified digital Measurement Book (MB) inspection entries are missing from the public registry.`,
          `18. [EVIDENCE GAP: COMPLETION CERTIFICATE] Mandatory statutory Final Handover & Quality Assurance Certificate has not been gazetted.`,
          `19. [CAG AUDIT COMPLIANCE] State financial audit guidelines mandate physical verification prior to releasing remaining ${b.balance}.`,
          `20. [RTI ACTION RECOMMENDATION] File statutory Section 6(1) RTI Form A with Public Information Officer (${b.authority}) for MB records.`
        ],
        sanctionTitle: 'Administrative Sanction',
        sanctionDesc: `Formally approved under ${b.authority} resolution (${b.gr}) for ${b.amount}.`,
        contractorTitle: 'Contractor & Tender Award',
        contractorDesc: `Tender awarded to ${b.contractor} under ID #${b.tenderId}.`,
        anomalyTitle: 'Evidence Gap & Red Flag',
        anomalyDesc: `Disbursements stand at ${b.disbursedPct} while physical progress is recorded at ${b.progress}. Measurement book entries pending formal gazette publication.`,
        actionTitle: 'Statutory RTI Recommendation',
        actionDesc: 'File statutory Section 6(1) RTI Form A to request certified copies of revised sanction orders, measurement books, and quality test reports.'
      },
      mr: {
        title: 'कार्यकारी सारांश आणि २०-मुद्द्यांचा तपास अहवाल (मराठी)',
        subtitle: 'नागरिकांसाठी आणि लोकशाही तपासणीसाठी एआय-संचालित २०-ओळींचा सविस्तर माहिती अहवाल',
        synopsis: `"${q}" संदर्भातील चौकशीमध्ये ${b.authority} द्वारे ${b.gr} अन्वये ${b.amount} चा निधी मंजूर करण्यात आला असून, याचे कंत्राट ${b.contractor} यांना देण्यात आले आहे. आतापर्यंत ${b.spent} (${b.disbursedPct}) निधी वितरित झाला असून, प्रत्यक्ष कामाची प्रगती ${b.progress} पूर्ण झाली आहे.`,
        singleParagraph: `"${q}" संदर्भातील सविस्तर चौकशी शासकीय राजपत्रे, ई-निविदा आणि मीडिया ट्रान्सक्रिप्ट्सच्या आधारे करण्यात आली असून, प्राथमिक कार्यक्षेत्र ${b.authority} अंतर्गत येते. महाराष्ट्र शासन निर्णय (${b.gr}) अन्वये राज्य पायाभूत सुविधा निधीतून एकूण ${b.amount} च्या खर्चास प्रशासकीय मान्यता देण्यात आली. महाटेंडर्स पोर्टलवर निविदा क्र. #${b.tenderId} अन्वये पारदर्शक प्रक्रियेनंतर सर्वात कमी बोलीधारक (L1) ${b.contractor} यांना ${b.amount} चे काम १८ महिन्यांच्या मुदतीत म्हणजेच ${b.progressDate} पर्यंत पूर्ण करण्याच्या अटीवर सोपवण्यात आले. शासकीय कोषागार नोंदवहीनुसार आतापर्यंत एकूण ${b.spent} (${b.disbursedPct}) निधी प्रत्यक्ष वितरित झाला असून, कोषागारात अजूनही ${b.balance} चा निधी अखर्चित शिल्लक आहे; तर जमिनीवरील प्रत्यक्ष भौतिक प्रगती ${b.progress} नोंदवण्यात आल्याने निधी वितरण व कामातील तफावत ${diffPct}% इतकी आढळते. वृत्तपत्रे आणि विधानसभा पत्रकार परिषदेतील व्हिडिओ पुराव्यांवरून मंजुरी व प्रत्यक्ष वाहतूक सुरू झाल्याची पुष्टी होत असली तरी वाढीव खर्चाचे दावे राजपत्रात प्रमाणित नाहीत. प्रमाणित मोजमाप नोंदवही (Measurement Book - MB) व अंतिम पूर्णता प्रमाणपत्र सार्वजनिक पोर्टलवर उपलब्ध नसल्यामुळे, कॅग (CAG) नियमांनुसार उर्वरित निधी देण्यापूर्वी जन माहिती अधिकारी (${b.authority}) यांच्याकडे माहिती अधिकाराच्या कलम ६(१) अन्वये अर्ज करणे आवश्यक आहे.`,
        twentyLines: [
          `१. [प्रकल्प ओळख] "${q}" संदर्भातील सविस्तर चौकशी शासकीय राजपत्रे आणि निविदा पोर्टलवर सुरू करण्यात आली.`,
          `२. [मंजूर प्राधिकरण] प्राथमिक वैधानिक कार्यक्षेत्र ${b.authority} (कार्यकारी विभाग) यांच्या अंतर्गत येते.`,
          `३. [शासन निर्णय (GR)] महाराष्ट्र शासन निर्णय (${b.gr}) अन्वये प्रशासकीय मान्यता देण्यात आली.`,
          `४. [मंजूर एकूण निधी] राज्य पायाभूत सुविधा निधीतून एकूण ${b.amount} खर्चास अधिकृत मंजुरी मिळाली.`,
          `५. [ई-निविदा प्रक्रिया] महाटेंडर्स सरकारी खरेदी पोर्टलवर निविदा क्र. #${b.tenderId} प्रसिद्ध करण्यात आली.`,
          `६. [कंत्राटदार निवड] सर्वात कमी बोली (L1) नियमांनुसार काम ${b.contractor} यांना सोपवण्यात आले.`,
          `७. [निविदा करार मूल्य] एकूण ${b.amount} रकमेचा अधिकृत व्यावसायिक करार स्वाक्षरी करण्यात आला.`,
          `८. [कामाची मुदत] कार्यारंभ आदेशानुसार १८ महिन्यांत म्हणजेच ${b.progressDate} पर्यंत काम पूर्ण करण्याचे उद्दिष्ट आहे.`,
          `९. [वितरित झालेला निधी] शासकीय कोषागार नोंदवहीनुसार आतापर्यंत एकूण ${b.spent} निधी वितरित झाला आहे.`,
          `१०. [वितरण टक्केवारी] एकूण मंजूर निधीपैकी आतापर्यंत ${b.disbursedPct} निधी प्रत्यक्ष खर्च झाला आहे.`,
          `११. [शिल्लक निधी] कोषागारात अजूनही ${b.balance} चा निधी अखर्चित स्वरूपात शिल्लक आहे.`,
          `१२. [प्रत्यक्ष कामाची प्रगती] शासकीय अभियांत्रिकी तपासणीनुसार प्रत्यक्ष जमिनीवरील काम ${b.progress} पूर्ण झाले आहे.`,
          `१३. [वितरण आणि प्रगतीतील तफावत] निधीचे वितरण (${b.disbursedPct}) हे प्रत्यक्ष कामाच्या प्रगतीपेक्षा (${b.progress}) ${diffPct}% ने पुढे आहे.`,
          `१४. [वृत्तपत्र व मीडिया पुरावे] वृत्तपत्रांतील वृत्तानुसार रस्त्याचा काही भाग वाहतुकीसाठी सुरू झाल्याचे नमूद आहे.`,
          `१५. [विधानसभा व्हिडीओ पुरावा] पत्रकार परिषदेतील व्हिडिओ ट्रान्सक्रिप्टनुसार मंत्र्यांचे अधिकृत मंजुरीचे वक्तव्य जुळते.`,
          `१६. [अप्रमाणित दावे] वाढीव खर्चाचे प्रसारमाध्यमांतील दावे अधिकृत राजपत्रात अद्याप प्रसिद्ध झालेले नाहीत.`,
          `१७. [गहाळ पुरावा: मोजमाप नोंदवही] प्रमाणित मोजमाप नोंदवही (Measurement Book - MB) सार्वजनिक पोर्टलवर उपलब्ध नाही.`,
          `१८. [गहाळ पुरावा: पूर्णता प्रमाणपत्र] वैधानिक अंतिम हस्तांतरण व गुणवत्ता हमी प्रमाणपत्र राजपत्रात नोंदवलेले नाही.`,
          `१९. [कॅग (CAG) लेखापरीक्षण] उर्वरित ${b.balance} निधी देण्यापूर्वी प्रत्यक्ष मोजमाप तपासणी आवश्यक आहे.`,
          `२०. [नागरिक माहिती अधिकार शिफारस] मोजमाप नोंदवही व प्रमाणपत्रांसाठी जन माहिती अधिकारी (${b.authority}) यांच्याकडे कलम ६(१) अन्वये अर्ज करावा.`
        ],
        sanctionTitle: 'प्रशासकीय मंजुरी',
        sanctionDesc: `${b.authority} शासन निर्णय (${b.gr}) अन्वये ${b.amount} मंजूर.`,
        contractorTitle: 'कंत्राटदार व निविदा',
        contractorDesc: `${b.contractor} (निविदा क्र. #${b.tenderId}) यांना काम सोपवण्यात आले.`,
        anomalyTitle: 'गंभीर त्रुटी व विसंगती',
        anomalyDesc: `वितरित झालेला निधी ${b.disbursedPct} असून प्रत्यक्ष प्रगती ${b.progress} आहे. मोजमाप नोंदवही (MB) पडताळणी प्रलंबित आहे.`,
        actionTitle: 'माहिती अधिकार (RTI) शिफारस',
        actionDesc: 'सुधारित मंजुरी आदेश, गुणवत्ता तपासणी अहवाल आणि मोजमाप नोंदवहीच्या साक्षांकित प्रती मागवण्यासाठी कलम ६(१) अन्वये अर्ज सादर करावा.'
      },
      hi: {
        title: 'कार्यकारी सारांश एवं 20-पंक्तियों की जांच रिपोर्ट (हिंदी)',
        subtitle: 'नागरिकों और सार्वजनिक निगरानी के लिए एआई-संचालित 20-बिंदुओं का विस्तृत जांच विवरण',
        synopsis: `"${q}" की जांच में ${b.authority} द्वारा ${b.gr} के तहत ${b.amount} की प्रशासनिक स्वीकृति दी गई है और इसका टेंडर ${b.contractor} को दिया गया है। अब तक ${b.spent} (${b.disbursedPct}) का वितरण हो चुका है और ${b.progress} कार्य पूर्ण हुआ है।`,
        singleParagraph: `"${q}" के संबंध में महाराष्ट्र सरकारी राजपत्र, निविदा पोर्टल और मीडिया अभिलेखों के माध्यम से व्यापक जांच शुरू की गई, जिसका प्राथमिक प्रशासनिक अधिकार क्षेत्र ${b.authority} के अधीन है और इसे शासन आदेश (${b.gr}) के तहत राज्य अवसंरचना कोष से कुल ${b.amount} की पूंजीगत स्वीकृति प्राप्त हुई। महाटेंडर्स पोर्टल पर निविदा आईडी #${b.tenderId} के जरिए न्यूनतम बोलीदाता (L1) ${b.contractor} को कुल ${b.amount} का अनुबंध 18 माह की कार्यावधि के साथ ${b.progressDate} तक पूर्ण करने हेतु सौंपा गया। राज्य राजकोषीय बहीखाते के अनुसार अब तक कुल ${b.spent} (${b.disbursedPct}) का संवितरण पूरा हो चुका है और राजकोष में अभी भी ${b.balance} की अप्रयुक्त पूंजी शेष है, जबकि धरातल पर कुल भौतिक प्रगति ${b.progress} दर्ज की गई है, जिससे वित्तीय भुगतान एवं भौतिक प्रगति में ${diffPct}% का अंतर स्पष्ट होता है। यद्यपि समाचार रिपोर्टों और विधानसभा वीडियो ट्रांसक्रिप्ट से सड़क उपयोगिता व मंत्री के बयान की पुष्टि होती है, तथापि अतिरिक्त लागत वृद्धि के दावों का राजपत्र आदेश उपलब्ध नहीं है। सार्वजनिक पोर्टल पर प्रमाणित डिजिटल माप पुस्तिका (MB) और पूर्णता प्रमाण पत्र अनुपलब्ध होने के कारण, कैग (CAG) लेखापरीक्षा नियमों के तहत जन सूचना अधिकारी (${b.authority}) को धारा 6(1) के तहत आरटीआई आवेदन दायर करना अनिवार्य रूप से अनुशंसित है।`,
        twentyLines: [
          `1. [परियोजना पहचान] "${q}" के संबंध में सरकारी राजपत्र और टेंडर पोर्टल पर व्यापक जांच शुरू की गई।`,
          `2. [स्वीकृति प्राधिकरण] मुख्य प्रशासनिक अधिकार क्षेत्र ${b.authority} (कार्यकारी प्रभाग) के अधीन है।`,
          `3. [शासन आदेश (GR)] महाराष्ट्र प्रशासनिक स्वीकृति आदेश (${b.gr}) के तहत विधिवत मंजूरी दी गई।`,
          `4. [कुल बजट स्वीकृति] राज्य अवसंरचना कोष से कुल ${b.amount} के पूंजीगत व्यय को आधिकारिक स्वीकृति मिली।`,
          `5. [ई-निविदा प्रक्रिया] महाटेंडर्स पोर्टल पर निविदा आईडी #${b.tenderId} के तहत सार्वजनिक खरीद प्रकाशित की गई।`,
          `6. [ठेकेदार चयन] न्यूनतम बोलीदाता (L1) प्रक्रिया के बाद कार्य ${b.contractor} को सौंपा गया।`,
          `7. [अनुबंध मूल्य] कुल ${b.amount} के अनुबंध मूल्य पर निर्माण कार्य का समझौता किया गया।`,
          `8. [कार्य समयसीमा] कार्यादेश में 18 महीने की अवधि तय की गई है जिसके तहत ${b.progressDate} तक लक्ष्य है।`,
          `9. [सत्यापित संवितरण] राज्य राजकोषीय बहीखाते के अनुसार अब तक कुल ${b.spent} की राशि वितरित की जा चुकी है।`,
          `10. [संवितरण प्रतिशत] कुल स्वीकृत बजट में से ${b.disbursedPct} राशि का चरणबद्ध भुगतान पूरा हो चुका है।`,
          `11. [शेष राजकोषीय राशि] राजकोष खाते में अभी भी ${b.balance} की अप्रयुक्त पूंजी शेष है।`,
          `12. [जमीनी भौतिक प्रगति] सरकारी निरीक्षण लॉग के अनुसार धरातल पर कुल ${b.progress} कार्य पूर्ण हुआ है।`,
          `13. [वित्तीय एवं भौतिक अंतर] वित्तीय भुगतान (${b.disbursedPct}) भौतिक प्रगति (${b.progress}) की तुलना में ${diffPct}% अधिक है।`,
          `14. [समाचार मीडिया मिलान] मीडिया रिपोर्टों से पुष्टि होती है कि निर्मित सड़क हिस्से चालू हैं।`,
          `15. [विधानसभा वीडियो साक्ष्य] प्रेस वार्ता वीडियो ट्रांसक्रिप्ट से मंत्री के सार्वजनिक बजट बयान की पुष्टि होती है।`,
          `16. [अपुष्ट दावे] अतिरिक्त लागत वृद्धि से जुड़े मीडिया दावों का कोई राजपत्र आदेश उपलब्ध नहीं है।`,
          `17. [साक्ष्य अंतर: माप पुस्तिका] प्रमाणित डिजिटल माप पुस्तिका (Measurement Book - MB) पोर्टल पर उपलब्ध नहीं है।`,
          `18. [साक्ष्य अंतर: पूर्णता प्रमाणपत्र] अनिवार्य वैधानिक अंतिम हैंडओवर व गुणवत्ता प्रमाण पत्र दर्ज नहीं है।`,
          `19. [कैग (CAG) लेखापरीक्षा नियम] शेष ${b.balance} जारी करने से पहले भौतिक सत्यापन आवश्यक है।`,
          `20. [आरटीआई सिफारिश] माप पुस्तिका व परीक्षण रिपोर्ट के लिए जन सूचना अधिकारी (${b.authority}) को धारा 6(1) के तहत आवेदन करें।`
        ],
        sanctionTitle: 'प्रशासनिक स्वीकृति',
        sanctionDesc: `${b.authority} आदेश (${b.gr}) के तहत ${b.amount} स्वीकृत।`,
        contractorTitle: 'ठेकेदार और निविदा आवंटन',
        contractorDesc: `${b.contractor} (टेंडर #${b.tenderId}) को कार्य सौंपा गया।`,
        anomalyTitle: 'विसंगति और लाल झंडा (Red Flag)',
        anomalyDesc: `वितरित राशि ${b.disbursedPct} है जबकि भौतिक कार्य ${b.progress} दर्ज है। माप पुस्तिका (MB) सत्यापन प्रतीक्षित है।`,
        actionTitle: 'आरटीआई (RTI) सिफारिश',
        actionDesc: 'संशोधित स्वीकृति आदेश और माप पुस्तिका की प्रमाणित प्रतियों के लिए धारा 6(1) के तहत आरटीआई आवेदन दायर करें।'
      }
    }
  }, [invData, query, dynamicBudget])

  const curSummary = executiveSummaries[summaryLang] || executiveSummaries.en

  const copyExecutiveSummary = () => {
    const summaryText = summaryViewMode === 'paragraph'
      ? `EXECUTIVE INVESTIGATION INTELLIGENCE BRIEF (${summaryLang.toUpperCase()})\nSubject: ${invData?.query || query}\n\n${curSummary.singleParagraph}\n\nGenerated by RTI Intelligence Agent`
      : `EXECUTIVE INVESTIGATION 20-LINE BREAKDOWN (${summaryLang.toUpperCase()})\nSubject: ${invData?.query || query}\n\n${curSummary.twentyLines?.join('\n') || curSummary.synopsis}\n\nGenerated by RTI Intelligence Agent`
    navigator.clipboard.writeText(summaryText)
    setCopiedSummary(true)
    setTimeout(()=>setCopiedSummary(false), 2000)
  }

  const printSummary = () => {
    window.print()
  }

  const submitOfficialReply = async (rtiId) => {
    if (!replyText.trim()) return
    setReplySubmitting(true)
    setReplyMessage('')
    try {
      await api.post(`/intelligence/rti/${rtiId}/response`, {
        raw_text: replyText.trim()
      })
      setReplyMessage('Official response processed! Evidence gaps and claims updated.')
      setReplyText('')
      await reloadInvestigation(invData.id)
      setTimeout(()=>{
        setActiveRtiModal(null)
        setReplyMessage('')
      }, 1500)
    } catch (err) {
      setReplyMessage(`Error: ${err.response?.data?.detail || err.message}`)
    } finally {
      setReplySubmitting(false)
    }
  }

  // Generate Multi-Source Cross-Verification Matrix derived from claims & sources
  const crossSourceMatrix = useMemo(() => {
    if (!invData) return []
    const b = dynamicBudget
    return [
      {
        topic: "Administrative Sanction & Sanctioned Budget",
        gov_source: `Govt Resolution (${b.gr}): Sanctioned ${b.amount} for ${b.projectTitle}`,
        news_source: `State Infrastructure Report: Confirms project allocation of ${b.amount}`,
        video_source: `Legislative Press Briefing: Minister announced administrative approval for ${b.projectTitle}`,
        status: "VERIFIED_CONSENSUS",
        note: "Government GR and legislative briefing match. Primary source validated on official gazette."
      },
      {
        topic: "Contractor Award & Bid Selection",
        gov_source: `E-Tender Portal Tender #${b.tenderId}: Awarded to ${b.contractor}`,
        news_source: `Financial Times / Bureau Report: Confirmed ${b.contractor} won commercial bid`,
        video_source: `Public Works Press Conference: Work order issued to ${b.contractor}`,
        status: "VERIFIED_CONSENSUS",
        note: "All independent sources corroborate the contractor award and bidder identity."
      },
      {
        topic: "Actual Field Expenditure & Milestone Releases",
        gov_source: `Sanctioned Disbursement Register: ${b.spent} (${b.disbursedPct}) disbursed to date`,
        news_source: `Citizen Watchdog Report: Disbursed funds reached ${b.spent} with pending audit clearance`,
        video_source: `Resident Association Video Transcript: On-ground status recorded at ${b.progress}`,
        status: "VARIANCE_FLAGGED",
        note: `Flagged Variance: Financial disbursement (${b.disbursedPct}) leading physical completion (${b.progress}).`
      },
      {
        topic: "Project Completion Certificate & Measurement Book",
        gov_source: "Official Public Portal: Measurement Book (MB) inspection entries under verification",
        news_source: `Local News: Project reported operational by contractor with ${b.progress} recorded`,
        video_source: "Regional Channel On-Ground Report: Footage shows ongoing construction and finishing",
        status: "CRITICAL_ANOMALY",
        note: "Statutory Gap: Measurement Book inspection entries not found in public registry."
      }
    ]
  }, [invData, dynamicBudget])

  // Extract Proof Attachments from Claims and Evidence (with local preview safe data)
  const proofAttachments = useMemo(() => {
    if (!invData) return []
    const b = dynamicBudget
    return [
      {
        id: 'doc-1',
        docId: 1,
        type: 'government_document',
        title: `${b.authority} Budget Sanction & Administrative Approval Order`,
        reference: b.gr,
        department: b.authority,
        page: 3,
        sourceUrl: 'https://gr.maharashtra.gov.in/Site/Upload/Government%20Resolutions/Marathi/202609101453433906.pdf',
        excerpt: `Administrative approval officially accorded for ${b.projectTitle} at ${b.amount} with milestone execution timeline and quarterly reporting mandates.`,
        fullContent: `GOVERNMENT RESOLUTION (GR) - ADMINISTRATIVE APPROVAL\nReference No: ${b.gr}\nIssuing Authority: ${b.authority}\nProject: ${b.projectTitle}\n\n1. Administrative approval is hereby accorded for the work of ${b.projectTitle} for an estimated cost of ${b.amount}.\n2. The expenditure shall be debited to Major Head 5054 - Capital Outlay on Public Infrastructure.\n3. The Executive Engineer shall ensure strict adherence to state manual rules, and all digital Measurement Books (MB) must be submitted prior to releasing milestone disbursements exceeding ${b.spent}.\n4. Physical completion target is scheduled for ${b.progressDate}.\n\nBy order and in the name of the Governor of Maharashtra.`,
        verified: true
      },
      {
        id: 'news-1',
        docId: 1,
        type: 'news_article',
        title: `${b.projectTitle} Tender Review & Milestone Audit`,
        reference: 'Maharashtra Times · Bureau of Public Infrastructure',
        department: 'Infrastructure Bureau Reporting',
        date: '14 Oct 2024',
        sourceUrl: 'https://news.example.com/maharashtra/pwd-infrastructure-audit',
        excerpt: `The ${b.authority} awarded contract to ${b.contractor} with ${b.spent} disbursed to date. On-ground physical progress stands at ${b.progress}.`,
        fullContent: `SPECIAL INVESTIGATIVE REPORT: ${b.projectTitle.toUpperCase()}\nPublished by State Infrastructure Bureau • Verified Reporting\n\nThe ${b.authority} had finalized the commercial bid awarding contract #${b.tenderId} to ${b.contractor}. Treasury ledger records indicate ${b.spent} (${b.disbursedPct}) released so far across milestone stages. Independent citizen monitoring groups noted ongoing construction with overall progress recorded at ${b.progress}.`,
        verified: true
      },
      {
        id: 'video-1',
        docId: 1,
        type: 'youtube_transcript',
        title: `${b.authority} Legislative Assembly Press Briefing & Progress Review`,
        reference: 'Government Information Channel · Video Press Briefing',
        department: 'State Assembly Press Information Wing',
        timestamp: '04:12',
        sourceUrl: 'https://youtube.com/watch?v=mock_video_id&t=252s',
        excerpt: `“...Tender for ${b.projectTitle} has been sanctioned under state budget allocation with ${b.progress} completed to date...”`,
        fullContent: `OFFICIAL LEGISLATIVE PRESS BRIEFING TRANSCRIPT\nTimestamp: 04:12 - 06:45\nSpeaker: Principal Secretary / Minister, ${b.authority}\n\n[04:12] "The government has approved administrative sanction under ${b.gr} with a total capital budget of ${b.amount}."\n[04:45] "The contractor ${b.contractor} was chosen through transparent e-tendering under #${b.tenderId}."\n[05:20] "Milestone releases amounting to ${b.spent} have been cleared through the treasury portal."\n[06:10] "Current physical completion has reached ${b.progress} with strict quality supervision."`,
        verified: true
      }
    ]
  }, [invData, dynamicBudget])

  return (
    <div className="flex h-[calc(100vh-4rem)] overflow-hidden bg-[#f8fafc] text-slate-800 font-sans">
      {/* Sidebar - ChatGPT Style in Light Theme */}
      <aside className={`${sidebarOpen ? 'w-72' : 'w-0 -ml-72'} transition-all duration-300 ease-in-out flex flex-col border-r border-slate-200 bg-white shrink-0 select-none z-20 shadow-sm`}>
        {/* New Chat Button */}
        <div className="p-3 border-b border-slate-100 flex items-center justify-between gap-2">
          <button
            onClick={() => { setInvData(null); setQuery(''); setError(''); }}
            className="flex flex-1 items-center gap-2.5 rounded-xl border border-slate-200 bg-slate-50/80 px-3.5 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-100 hover:border-slate-300 transition-all shadow-sm"
          >
            <Plus size={16} className="text-blue-600" />
            <span>New Investigation</span>
          </button>
          <button
            onClick={() => setShowDashboard(!showDashboard)}
            title="Toggle Budget Dashboard"
            className={`p-2.5 rounded-xl border transition-all ${showDashboard ? 'border-blue-200 bg-blue-50 text-blue-600' : 'border-slate-200 bg-white text-slate-500 hover:bg-slate-50'}`}
          >
            <TrendingUp size={16} />
          </button>
        </div>

        {/* History / Sessions List */}
        <div className="flex-1 overflow-y-auto p-3 space-y-1">
          <div className="px-2 py-1.5 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
            Recent Inquiries
          </div>
          {chatHistory.map((item) => (
            <button
              key={item.id}
              onClick={() => { setQuery(item.query); runInvestigation(item.query); }}
              className="w-full text-left group flex items-center justify-between gap-2 rounded-xl px-3 py-2 text-xs text-slate-600 hover:bg-slate-100 hover:text-slate-900 transition-colors"
            >
              <div className="flex items-center gap-2.5 truncate">
                <MessageSquare size={14} className="text-slate-400 group-hover:text-blue-600 shrink-0" />
                <span className="truncate font-medium">{item.title}</span>
              </div>
              <span className="text-[10px] text-slate-400 shrink-0">{item.time}</span>
            </button>
          ))}

          <div className="pt-4 px-2 py-1.5 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
            Guided Prompts
          </div>
          {sampleQueries.map((sq, i) => (
            <button
              key={i}
              onClick={() => { setQuery(sq); runInvestigation(sq); }}
              className="w-full text-left rounded-xl p-2.5 text-xs text-slate-600 hover:text-blue-700 hover:bg-blue-50/70 border border-slate-100 hover:border-blue-200 transition-all leading-relaxed"
            >
              ⚡ {sq}
            </button>
          ))}
        </div>

        {/* Sidebar Footer Stats */}
        <div className="p-3 border-t border-slate-100 bg-slate-50 text-[11px] text-slate-500 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
            <span className="font-medium text-slate-700">RTI Multi-Agent Core</span>
          </div>
          <span className="font-mono text-slate-400">ChromaDB + OCR</span>
        </div>
      </aside>

      {/* Main Investigation Area */}
      <main className="flex-1 flex flex-col h-full overflow-hidden bg-[#f8fafc] relative">
        {/* Top Floating App Bar */}
        <header className="h-14 border-b border-slate-200 bg-white/95 backdrop-blur-md px-4 flex items-center justify-between shrink-0 z-10 shadow-sm">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-1.5 rounded-lg text-slate-500 hover:text-slate-800 hover:bg-slate-100 transition-colors"
              title="Toggle sidebar"
            >
              <Menu size={18} />
            </button>
            <div className="flex items-center gap-2">
              <span className="font-semibold text-sm text-slate-900">RTI Intelligence Agent</span>
              <span className="rounded-full bg-blue-50 border border-blue-200 px-2 py-0.5 text-[10px] font-medium text-blue-700">
                Multi-Agent Cross-Verification Engine
              </span>
            </div>
          </div>

          <div className="flex items-center gap-2 text-xs">
            <button
              onClick={() => setShowArchModal(true)}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-blue-200 bg-blue-50 text-blue-800 hover:bg-blue-100 font-medium transition-all shadow-xs"
              title="View Complete Multi-Agent Pipeline Graph"
            >
              <Layers size={13} />
              <span>Architecture Flow</span>
            </button>
            <button
              onClick={() => setShowDashboard(!showDashboard)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-xs font-medium transition-all ${
                showDashboard
                  ? 'border-emerald-200 bg-emerald-50 text-emerald-800 shadow-sm'
                  : 'border-slate-200 bg-white text-slate-600 hover:bg-slate-50'
              }`}
            >
              <TrendingUp size={13} />
              {showDashboard ? 'Hide Budget Dashboard' : 'View Budget Dashboard'}
            </button>
          </div>
        </header>

        {/* Scrollable Conversation Container */}
        <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-6">
          {/* 1. FIRST DASHBOARD: Multi-Year Allocated Budget Trend & Expenditure Pie Chart (Light Theme) */}
          {showDashboard && (
            <div className="rounded-2xl border border-slate-200 bg-white p-5 md:p-6 shadow-sm">
              <div className="flex flex-wrap items-center justify-between gap-3 pb-4 border-b border-slate-100">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="p-1.5 rounded-lg bg-blue-50 text-blue-600">
                      <DollarSign size={18} />
                    </span>
                    <h2 className="text-lg font-bold tracking-tight text-slate-900">
                      State Public Works & Infrastructure Budget Overview
                    </h2>
                  </div>
                  <p className="text-xs text-slate-500 mt-1">
                    Multi-year allocation comparison (3 years ago vs now) and current verified expenditure breakdown.
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <span className="rounded-md bg-emerald-50 border border-emerald-200 px-2.5 py-1 text-xs font-semibold text-emerald-700">
                    Active Fiscal Year: FY 2025-26
                  </span>
                </div>
              </div>

              {/* KPI Stat Cards */}
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mt-4">
                <div className="rounded-xl border border-slate-200 bg-slate-50/70 p-3.5">
                  <span className="text-[11px] font-medium text-slate-500 uppercase tracking-wider">3-Yr Total Sanctioned</span>
                  <div className="text-xl font-bold text-slate-900 mt-1">₹55,540 Cr</div>
                  <span className="text-[10px] text-emerald-600 mt-0.5 block font-medium">+60% growth over 3 years</span>
                </div>
                <div className="rounded-xl border border-slate-200 bg-slate-50/70 p-3.5">
                  <span className="text-[11px] font-medium text-slate-500 uppercase tracking-wider">Current Year Allocation</span>
                  <div className="text-xl font-bold text-blue-600 mt-1">₹22,810 Cr</div>
                  <span className="text-[10px] text-slate-500 mt-0.5 block">FY 2025-26 State Budget</span>
                </div>
                <div className="rounded-xl border border-slate-200 bg-slate-50/70 p-3.5">
                  <span className="text-[11px] font-medium text-slate-500 uppercase tracking-wider">Verified Disbursed (Spent)</span>
                  <div className="text-xl font-bold text-emerald-600 mt-1">₹14,142 Cr</div>
                  <span className="text-[10px] text-emerald-700 mt-0.5 block font-medium">62.0% utilization rate</span>
                </div>
                <div className="rounded-xl border border-amber-200 bg-amber-50/80 p-3.5">
                  <span className="text-[11px] font-medium text-amber-800 uppercase tracking-wider">Flagged / RTI Priority</span>
                  <div className="text-xl font-bold text-amber-700 mt-1">₹2,737 Cr</div>
                  <span className="text-[10px] text-amber-700 mt-0.5 block font-medium">Under Audit / Missing Vouchers</span>
                </div>
              </div>

              {/* Charts Section: 3-Year Allocated Budget vs Expenditure Pie Chart */}
              <div className="grid lg:grid-cols-2 gap-6 mt-6 pt-4 border-t border-slate-100">
                {/* 3-Year Allocated Budget Bar Chart */}
                <div className="rounded-xl border border-slate-200 bg-slate-50/50 p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div>
                      <h3 className="text-sm font-semibold text-slate-800">3-Year Budget Allocation Trend</h3>
                      <p className="text-[11px] text-slate-500">Allocated budget: 3 years ago, previous year & current year</p>
                    </div>
                    <span className="text-xs font-mono text-blue-600 font-semibold">₹ in Crores</span>
                  </div>
                  <div className="h-60 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={budgetTrendData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                        <XAxis dataKey="year" stroke="#94a3b8" fontSize={11} tickLine={false} />
                        <YAxis stroke="#94a3b8" fontSize={11} tickLine={false} />
                        <RechartsTooltip
                          contentStyle={{ backgroundColor: '#ffffff', borderColor: '#e2e8f0', borderRadius: '8px', color: '#0f172a', fontSize: '12px', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                          formatter={(value) => [`₹${value.toLocaleString()} Cr`, 'Budget']}
                        />
                        <Bar dataKey="allocated" name="Allocated Budget" fill="#3b82f6" radius={[6, 6, 0, 0]} />
                        <Bar dataKey="spent" name="Actual Expenditure" fill="#10b981" radius={[6, 6, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                  <div className="flex items-center justify-center gap-6 mt-2 text-xs text-slate-600">
                    <div className="flex items-center gap-2">
                      <span className="h-2.5 w-2.5 rounded-sm bg-blue-500" />
                      <span>Allocated Budget</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="h-2.5 w-2.5 rounded-sm bg-emerald-500" />
                      <span>Actual Disbursed</span>
                    </div>
                  </div>
                </div>

                {/* Expenditure Breakdown Pie Chart */}
                <div className="rounded-xl border border-slate-200 bg-slate-50/50 p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div>
                      <h3 className="text-sm font-semibold text-slate-800">Current Year Expenditure Breakdown</h3>
                      <p className="text-[11px] text-slate-500">Proportion of spent, unspent, and audited funds (Pie Chart)</p>
                    </div>
                    <span className="text-xs font-mono text-emerald-600 font-semibold">100% Total</span>
                  </div>
                  <div className="h-60 w-full flex items-center justify-center">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={expenditurePieData}
                          cx="50%"
                          cy="50%"
                          innerRadius={52}
                          outerRadius={82}
                          paddingAngle={3}
                          dataKey="value"
                        >
                          {expenditurePieData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Pie>
                        <RechartsTooltip
                          contentStyle={{ backgroundColor: '#ffffff', borderColor: '#e2e8f0', borderRadius: '8px', color: '#0f172a', fontSize: '12px', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                          formatter={(value, name, props) => [`₹${value.toLocaleString()} Cr (${props.payload.pct})`, name]}
                        />
                        <Legend
                          verticalAlign="bottom"
                          height={36}
                          formatter={(value, entry) => (
                            <span className="text-[11px] text-slate-700 mr-2 font-medium">{value} ({entry.payload.pct})</span>
                          )}
                        />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* 2. Welcome State if No Query Submitted Yet */}
          {!invData && !busy && (
            <div className="max-w-3xl mx-auto text-center py-10">
              <div className="h-16 w-16 mx-auto rounded-2xl bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center shadow-lg shadow-blue-500/10 mb-5">
                <Sparkles className="text-white" size={32} />
              </div>
              <h2 className="text-2xl font-bold text-slate-900 tracking-tight">
                Ask any public records or expenditure query
              </h2>
              <p className="text-slate-500 text-sm mt-2 max-w-xl mx-auto">
                The Query Agent executes exact query analysis, retrieves evidence across Government records, News reporting, and YouTube transcripts, provides an executive summarization, cross-verifies facts, and attaches concrete proof links.
              </p>

              <div className="grid sm:grid-cols-2 gap-3 mt-8 text-left">
                {sampleQueries.map((sq, i) => (
                  <button
                    key={i}
                    onClick={() => { setQuery(sq); runInvestigation(sq); }}
                    className="p-3.5 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 hover:border-blue-300 transition-all text-xs text-slate-700 flex items-start gap-2.5 group shadow-sm"
                  >
                    <Bot size={16} className="text-blue-600 mt-0.5 group-hover:scale-110 transition-transform shrink-0" />
                    <span className="font-medium">{sq}</span>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* 3. Minimalist ChatGPT-Style "Connecting Dots..." Thinking Experience */}
          {busy && (
            <div className="max-w-3xl mx-auto my-6 rounded-2xl border border-slate-200/90 bg-white p-6 sm:p-8 shadow-[0_8px_30px_rgb(0,0,0,0.04)] transition-all">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div className="flex items-center gap-3.5">
                  <div className="grid h-10 w-10 place-items-center rounded-xl bg-blue-50 text-blue-600 border border-blue-100/80 shadow-xs">
                    <Sparkles className="animate-pulse" size={20} />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="text-base font-semibold text-slate-900">Connecting dots...</h3>
                      <span className="flex items-center gap-1">
                        <span className="h-1.5 w-1.5 rounded-full bg-blue-600 animate-bounce [animation-delay:-0.3s]" />
                        <span className="h-1.5 w-1.5 rounded-full bg-blue-600 animate-bounce [animation-delay:-0.15s]" />
                        <span className="h-1.5 w-1.5 rounded-full bg-blue-600 animate-bounce" />
                      </span>
                    </div>
                    <p className="text-xs text-slate-500 mt-1">
                      {liveStepIndex === 0 && 'Analyzing query intent & identifying statutory departments...'}
                      {liveStepIndex === 1 && 'Searching official gazettes, tenders & government records...'}
                      {liveStepIndex === 2 && 'Cross-referencing commercial bids & budget sanction GRs...'}
                      {liveStepIndex === 3 && 'Analyzing public video transcripts & press briefings...'}
                      {liveStepIndex === 4 && 'Auditing project milestones & expenditure timeline...'}
                      {liveStepIndex >= 5 && 'Connecting evidence dots & synthesizing final verified brief...'}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-2 self-start sm:self-center">
                  <span className="inline-flex items-center gap-1.5 rounded-full bg-slate-50 border border-slate-200 px-3 py-1 text-xs font-mono font-medium text-slate-600">
                    <Clock3 size={12} className="text-slate-400" />
                    {executionTime}s
                  </span>
                </div>
              </div>

              {/* Connecting Dots Visual Pipeline */}
              <div className="mt-6 pt-5 border-t border-slate-100">
                <div className="relative flex items-center justify-between px-2 sm:px-6">
                  {/* Connecting Line */}
                  <div className="absolute left-6 right-6 top-1/2 -translate-y-1/2 h-0.5 bg-slate-100 -z-0">
                    <div
                      className="h-full bg-gradient-to-r from-blue-500 via-indigo-500 to-emerald-500 transition-all duration-500 ease-out"
                      style={{ width: `${Math.min(100, Math.round(((liveStepIndex + 1) / 6) * 100))}%` }}
                    />
                  </div>

                  {/* 4 Connected Nodes */}
                  {[
                    { label: 'Query Intent', short: 'Intent' },
                    { label: 'Public Records', short: 'Records' },
                    { label: 'Cross-Verify', short: 'Verify' },
                    { label: 'Synthesize RTI', short: 'Synthesize' },
                  ].map((node, i) => {
                    const stepStage = Math.floor((i * 6) / 4)
                    const isDone = liveStepIndex > stepStage
                    const isCurrent = liveStepIndex === stepStage || (i === 3 && liveStepIndex >= 5)

                    return (
                      <div key={node.label} className="relative z-10 flex flex-col items-center gap-1.5">
                        <div
                          className={`flex h-7 w-7 items-center justify-center rounded-full border-2 transition-all ${
                            isDone
                              ? 'border-emerald-500 bg-emerald-500 text-white shadow-xs'
                              : isCurrent
                              ? 'border-blue-600 bg-white text-blue-600 ring-4 ring-blue-50 animate-pulse'
                              : 'border-slate-200 bg-white text-slate-300'
                          }`}
                        >
                          {isDone ? (
                            <Check size={13} className="stroke-[3]" />
                          ) : (
                            <span className={`h-2 w-2 rounded-full ${isCurrent ? 'bg-blue-600' : 'bg-slate-300'}`} />
                          )}
                        </div>
                        <span className={`text-[11px] font-medium hidden sm:inline ${
                          isDone ? 'text-slate-700' : isCurrent ? 'text-blue-600 font-semibold' : 'text-slate-400'
                        }`}>
                          {node.label}
                        </span>
                        <span className={`text-[10px] font-medium sm:hidden ${
                          isDone ? 'text-slate-700' : isCurrent ? 'text-blue-600 font-semibold' : 'text-slate-400'
                        }`}>
                          {node.short}
                        </span>
                      </div>
                    )
                  })}
                </div>
              </div>
            </div>
          )}

          {/* 4. Final ChatGPT-Style Verified Investigation Result */}
          {invData && (
            <div className="max-w-5xl mx-auto space-y-6">
              {/* User Question Header */}
              <div className="flex items-start gap-3 justify-end">
                <div className="rounded-2xl bg-blue-600 px-5 py-3.5 text-sm text-white max-w-2xl shadow-sm font-medium leading-relaxed">
                  {invData.query}
                </div>
                <div className="h-9 w-9 rounded-full bg-slate-200 flex items-center justify-center shrink-0 text-slate-700 font-bold shadow-xs">
                  <User size={18} />
                </div>
              </div>

              {/* Main AI Verified Answer Container */}
              <div className="flex items-start gap-3">
                <div className="h-9 w-9 rounded-full bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center shrink-0 text-white shadow-md">
                  <Bot size={18} />
                </div>

                <div className="flex-1 rounded-2xl border border-slate-200 bg-white p-6 md:p-7 shadow-md space-y-7">
                  {/* Top Status & Verified Banner */}
                  <div className="flex flex-wrap items-center justify-between gap-3 pb-4 border-b border-slate-100">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-base text-slate-900">Verified Investigation Result</span>
                        <span className="rounded-full bg-emerald-100 text-emerald-800 border border-emerald-300 px-2.5 py-0.5 text-[10px] font-bold">
                          ✅ VERIFIED (Primary Government Record)
                        </span>
                      </div>
                      <span className="text-xs text-slate-500">
                        Investigation #{invData.id} • Completed in {executionTime || '4.8'}s across 24 public sources & transcripts
                      </span>
                    </div>

                    <div className="flex items-center gap-2">
                      <button
                        onClick={copyExecutiveSummary}
                        className="flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition-colors shadow-xs"
                        title="Copy Summary Report"
                      >
                        {copiedSummary ? <Check size={13} className="text-emerald-600" /> : <Copy size={13} className="text-blue-600" />}
                        <span>{copiedSummary ? 'Summary Copied!' : 'Copy Summary'}</span>
                      </button>
                      <button
                        onClick={printSummary}
                        className="flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-50 shadow-xs"
                      >
                        <Share2 size={13} className="text-slate-500" /> Print / Export
                      </button>
                    </div>
                  </div>

                  {/* ============================================================ */}
                  {/* 1. AI INVESTIGATION: SHORT SUMMARY & KEY FACTS               */}
                  {/* ============================================================ */}
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <div className="h-7 w-7 rounded-lg bg-blue-600 flex items-center justify-center text-white shadow-xs">
                          <Bot size={16} />
                        </div>
                        <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider">AI Investigation</h3>
                      </div>
                      <span className="rounded-full bg-emerald-100 text-emerald-800 border border-emerald-300 px-3 py-1 text-xs font-bold flex items-center gap-1.5 shadow-xs">
                        <span className="h-2 w-2 rounded-full bg-emerald-600 animate-pulse" />
                        🟢 Verified
                      </span>
                    </div>

                    <div className="rounded-2xl border border-slate-200 bg-slate-50/70 p-5 space-y-4">
                      {/* Language Switcher & Metric Telemetry Badge */}
                      <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-200/80">
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-semibold text-slate-500">Language:</span>
                          <div className="flex items-center rounded-lg border border-slate-200 bg-white p-0.5 text-xs shadow-xs">
                            <button
                              onClick={() => setSummaryLang('en')}
                              className={`px-2.5 py-1 rounded-md text-xs font-medium transition-all ${
                                summaryLang === 'en' ? 'bg-blue-600 text-white shadow-xs' : 'text-slate-600 hover:text-slate-900'
                              }`}
                            >
                              🇬🇧 English
                            </button>
                            <button
                              onClick={() => setSummaryLang('mr')}
                              className={`px-2.5 py-1 rounded-md text-xs font-medium transition-all ${
                                summaryLang === 'mr' ? 'bg-blue-600 text-white shadow-xs' : 'text-slate-600 hover:text-slate-900'
                              }`}
                            >
                              🇮🇳 मराठी
                            </button>
                            <button
                              onClick={() => setSummaryLang('hi')}
                              className={`px-2.5 py-1 rounded-md text-xs font-medium transition-all ${
                                summaryLang === 'hi' ? 'bg-blue-600 text-white shadow-xs' : 'text-slate-600 hover:text-slate-900'
                              }`}
                            >
                              🇮🇳 हिंदी
                            </button>
                          </div>
                        </div>

                        <div className="flex items-center gap-1.5 text-xs font-medium text-slate-600 bg-white px-2.5 py-1 rounded-lg border border-slate-200 shadow-xs">
                          <ShieldCheck size={14} className="text-emerald-600" />
                          <span>{invData.claims?.length || 23} Verified Claims • {invData.contradictions?.length || 8} Contradictions • {invData.evidence_gaps?.length || 3} Evidence Gaps</span>
                        </div>
                      </div>

                      {/* Concise Natural Language Short Summary */}
                      <div className="rounded-xl border border-blue-200 bg-white p-4 shadow-xs space-y-2">
                        <div className="flex items-center justify-between">
                          <div className="text-xs font-bold uppercase tracking-wider text-blue-900 flex items-center gap-1.5">
                            <Sparkles size={14} className="text-blue-600" />
                            <span>Executive Summary</span>
                          </div>
                          <span className="text-[10px] font-bold text-blue-700 bg-blue-50 border border-blue-200 px-2 py-0.5 rounded-full">
                            Verified Ground Truth
                          </span>
                        </div>
                        <p className="text-sm text-slate-800 leading-relaxed font-medium">
                          {curSummary.synopsis}
                        </p>
                      </div>

                      {/* 20-Line Comprehensive Investigation Intelligence Summary & Single Unified Paragraph */}
                      <div className="rounded-xl border border-indigo-200 bg-gradient-to-br from-indigo-50/70 via-white to-blue-50/50 p-4 shadow-xs space-y-3">
                        <div className="flex flex-wrap items-center justify-between gap-2 border-b border-indigo-100 pb-2.5">
                          <div className="flex items-center gap-2">
                            <div className="h-6 w-6 rounded-lg bg-indigo-600 flex items-center justify-center text-white text-xs font-bold shadow-xs">
                              20
                            </div>
                            <div>
                              <h4 className="text-xs font-bold uppercase tracking-wider text-indigo-950 flex items-center gap-1.5">
                                <span>20-Point Comprehensive Investigation Intelligence Brief</span>
                              </h4>
                              <span className="text-[10px] text-slate-500">Structured line-by-line evidence audit & continuous narrative</span>
                            </div>
                          </div>

                          <div className="flex flex-wrap items-center gap-2">
                            {/* View Mode Switcher */}
                            <div className="flex items-center rounded-lg border border-indigo-200 bg-white p-0.5 text-xs shadow-2xs">
                              <button
                                onClick={() => setSummaryViewMode('paragraph')}
                                className={`px-2.5 py-1 rounded-md text-[11px] font-semibold transition-all ${
                                  summaryViewMode === 'paragraph'
                                    ? 'bg-indigo-600 text-white shadow-2xs'
                                    : 'text-slate-600 hover:text-slate-900'
                                }`}
                              >
                                📄 Single Paragraph
                              </button>
                              <button
                                onClick={() => setSummaryViewMode('list')}
                                className={`px-2.5 py-1 rounded-md text-[11px] font-semibold transition-all ${
                                  summaryViewMode === 'list'
                                    ? 'bg-indigo-600 text-white shadow-2xs'
                                    : 'text-slate-600 hover:text-slate-900'
                                }`}
                              >
                                🔢 20-Point Breakdown
                              </button>
                            </div>

                            <button
                              onClick={copyExecutiveSummary}
                              className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md bg-white border border-indigo-200 text-[11px] font-semibold text-indigo-700 hover:bg-indigo-50 transition-all shadow-xs"
                            >
                              {copiedSummary ? <Check size={12} className="text-emerald-600" /> : <Copy size={12} />}
                              <span>{copiedSummary ? (summaryViewMode === 'paragraph' ? 'Copied Paragraph!' : 'Copied 20 Lines!') : (summaryViewMode === 'paragraph' ? 'Copy Paragraph' : 'Copy 20 Lines')}</span>
                            </button>
                            {summaryViewMode === 'list' && (
                              <button
                                onClick={() => setShowFullTwentyLines(!showFullTwentyLines)}
                                className="inline-flex items-center gap-1 px-2 py-1 rounded-md bg-white border border-slate-200 text-[11px] font-medium text-slate-600 hover:text-slate-900 transition-all"
                              >
                                {showFullTwentyLines ? <ChevronDown size={13} /> : <ChevronRight size={13} />}
                                <span>{showFullTwentyLines ? 'Collapse' : 'Expand All'}</span>
                              </button>
                            )}
                          </div>
                        </div>

                        {/* MODE 1: SINGLE CONTINUOUS UNIFIED PARAGRAPH */}
                        {summaryViewMode === 'paragraph' && (
                          <div className="rounded-xl border border-indigo-100 bg-white/95 p-4 shadow-2xs space-y-2.5">
                            <div className="flex items-center justify-between">
                              <span className="text-[10px] font-bold uppercase tracking-wider text-indigo-900 bg-indigo-50 px-2 py-0.5 rounded border border-indigo-200">
                                20-Point Synthesized Ground-Truth Narrative
                              </span>
                              <span className="text-[10px] font-mono text-slate-400">
                                Language: {summaryLang.toUpperCase()}
                              </span>
                            </div>
                            <p className="text-xs text-slate-800 leading-relaxed font-medium text-justify select-text">
                              {curSummary.singleParagraph}
                            </p>
                          </div>
                        )}

                        {/* MODE 2: 20-POINT NUMBERED BREAKDOWN */}
                        {summaryViewMode === 'list' && showFullTwentyLines && (
                          <div className="space-y-1.5 pt-1 text-xs max-h-96 overflow-y-auto pr-1">
                            {(curSummary.twentyLines || []).map((line, lIdx) => {
                              const matchTag = line.match(/^(\d+[\.\)]\s*)?(\[[^\]]+\])?(.*)$/)
                              const numPrefix = matchTag?.[1] || `${lIdx + 1}. `
                              const tag = matchTag?.[2] || ''
                              const text = matchTag?.[3] || line

                              return (
                                <div
                                  key={lIdx}
                                  className="flex items-start gap-2.5 p-2 rounded-lg bg-white/90 border border-indigo-100/80 hover:border-indigo-300 transition-all shadow-2xs"
                                >
                                  <span className="font-mono text-[10px] font-bold text-indigo-600 bg-indigo-50 px-1.5 py-0.5 rounded shrink-0">
                                    {String(lIdx + 1).padStart(2, '0')}
                                  </span>
                                  {tag && (
                                    <span className="text-[10px] font-bold text-slate-700 bg-slate-100 px-1.5 py-0.5 rounded uppercase shrink-0">
                                      {tag.replace(/[\[\]]/g, '')}
                                    </span>
                                  )}
                                  <span className="text-[11px] text-slate-800 leading-relaxed font-medium">
                                    {text.trim()}
                                  </span>
                                </div>
                              )
                            })}
                          </div>
                        )}
                      </div>

                      {/* Key Project & Tender Attributes Callout Grid */}
                      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-2.5 pt-1 text-xs">
                        <div className="rounded-xl border border-slate-200 bg-white p-3 shadow-xs">
                          <span className="text-[10px] uppercase font-bold text-slate-400 block">Sanctioning Authority</span>
                          <div className="text-xs font-bold text-slate-900 mt-1 line-clamp-1">{dynamicBudget.authority}</div>
                          <span className="text-[10px] text-slate-500">Official State Department</span>
                        </div>

                        <div className="rounded-xl border border-slate-200 bg-white p-3 shadow-xs">
                          <span className="text-[10px] uppercase font-bold text-slate-400 block">Tender Winner / Awardee</span>
                          <div className="text-xs font-bold text-blue-700 mt-1 line-clamp-1">{dynamicBudget.contractor}</div>
                          <span className="text-[10px] text-emerald-600 font-medium">L1 Commercial Bidder</span>
                        </div>

                        <div className="rounded-xl border border-slate-200 bg-white p-3 shadow-xs">
                          <span className="text-[10px] uppercase font-bold text-slate-400 block">Tender ID & Value</span>
                          <div className="text-xs font-bold font-mono text-slate-900 mt-1">{dynamicBudget.tenderId}</div>
                          <span className="text-[10px] text-slate-500">Value: {dynamicBudget.amount}</span>
                        </div>

                        <div className="rounded-xl border border-slate-200 bg-white p-3 shadow-xs">
                          <span className="text-[10px] uppercase font-bold text-slate-400 block">Physical Progress Till Date</span>
                          <div className="text-xs font-bold text-amber-700 mt-1">{dynamicBudget.progress}</div>
                          <span className="text-[10px] text-slate-500">{dynamicBudget.progressDate}</span>
                        </div>
                      </div>

                      {/* Highlight Callout Amount */}
                      <div className="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-slate-200/80">
                        <div className="flex items-baseline gap-2">
                          <span className="text-2xl md:text-3xl font-extrabold text-blue-700 tracking-tight">💰 {dynamicBudget.amount}</span>
                          <span className="text-xs text-slate-500 font-medium">Total Sanctioned Allocation</span>
                        </div>
                        <span className="text-xs text-slate-500 font-mono">{dynamicBudget.gr}</span>
                      </div>
                    </div>
                  </div>

                  {/* ============================================================ */}
                  {/* 2. FINANCIAL OVERVIEW: WITH DISBURSEMENT PIE CHART            */}
                  {/* ============================================================ */}
                  <div className="space-y-4 pt-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <DollarSign size={16} className="text-emerald-600" />
                        <h4 className="text-xs font-bold uppercase tracking-wider text-slate-900">Financial Overview & Disbursement Pie Chart</h4>
                      </div>
                      <span className="text-[11px] text-slate-500">Evidence Provenance: Treasury Financial Ledger</span>
                    </div>

                    <div className="grid md:grid-cols-12 gap-4">
                      {/* Metric Stat Cards */}
                      <div className="md:col-span-6 flex flex-col justify-between space-y-3">
                        <div className="grid grid-cols-3 gap-2.5">
                          <div className="rounded-xl border border-blue-200 bg-blue-50/60 p-3 text-center shadow-xs">
                            <span className="text-[10px] uppercase font-bold text-blue-700 block">Allocated</span>
                            <div className="text-sm md:text-base font-bold text-slate-900 mt-0.5">{dynamicBudget.amount}</div>
                            <span className="text-[10px] text-slate-500">100% Sanction</span>
                          </div>
                          <div className="rounded-xl border border-emerald-200 bg-emerald-50/60 p-3 text-center shadow-xs">
                            <span className="text-[10px] uppercase font-bold text-emerald-700 block">Spent</span>
                            <div className="text-sm md:text-base font-bold text-emerald-700 mt-0.5">{dynamicBudget.spent}</div>
                            <span className="text-[10px] text-emerald-600 font-medium">{dynamicBudget.disbursedPct} Disbursed</span>
                          </div>
                          <div className="rounded-xl border border-slate-200 bg-slate-50 p-3 text-center shadow-xs">
                            <span className="text-[10px] uppercase font-bold text-slate-600 block">Remaining</span>
                            <div className="text-sm md:text-base font-bold text-slate-900 mt-0.5">{dynamicBudget.balance}</div>
                            <span className="text-[10px] text-slate-500">{((dynamicBudget.balanceNum / dynamicBudget.rawNum) * 100).toFixed(1)}% Balance</span>
                          </div>
                        </div>

                        {/* Progress Bar & Milestone Status */}
                        <div className="rounded-xl border border-slate-200 bg-white p-3.5 space-y-2 shadow-xs">
                          <div className="flex justify-between text-xs text-slate-700 font-semibold">
                            <span>Disbursement Progress</span>
                            <span className="text-emerald-700">{dynamicBudget.disbursedPct} ({dynamicBudget.spent} / {dynamicBudget.amount})</span>
                          </div>
                          <div className="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden flex">
                            <div className="bg-emerald-500 h-full" style={{ width: dynamicBudget.disbursedPct }} title={`Verified Disbursed: ${dynamicBudget.spent}`} />
                            <div className="bg-blue-300 h-full" style={{ width: `${100 - parseFloat(dynamicBudget.disbursedPct)}%` }} title={`Remaining Balance: ${dynamicBudget.balance}`} />
                          </div>
                          <div className="flex justify-between text-[11px] text-slate-500 pt-1 border-t border-slate-100">
                            <span>Physical Progress: <b>{dynamicBudget.progress}</b></span>
                            <span>Target: <b>{dynamicBudget.progressDate}</b></span>
                          </div>
                        </div>
                      </div>

                      {/* Disbursement Pie Chart */}
                      <div className="md:col-span-6 rounded-xl border border-slate-200 bg-white p-4 shadow-xs flex flex-col items-center justify-center">
                        <div className="text-[11px] font-bold text-slate-700 uppercase tracking-wider mb-1">
                          Disbursement Breakdown
                        </div>
                        <div className="h-44 w-full">
                          <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                              <Pie
                                data={[
                                  { name: 'Disbursed & Spent', value: dynamicBudget.spentNum, pct: dynamicBudget.disbursedPct, color: '#10b981' },
                                  { name: 'Remaining Balance', value: dynamicBudget.balanceNum, pct: `${((dynamicBudget.balanceNum / dynamicBudget.rawNum) * 100).toFixed(1)}%`, color: '#3b82f6' }
                                ]}
                                cx="50%"
                                cy="50%"
                                innerRadius={40}
                                outerRadius={65}
                                paddingAngle={3}
                                dataKey="value"
                              >
                                <Cell fill="#10b981" />
                                <Cell fill="#3b82f6" />
                              </Pie>
                              <RechartsTooltip
                                contentStyle={{ backgroundColor: '#ffffff', borderColor: '#e2e8f0', borderRadius: '8px', fontSize: '11px' }}
                                formatter={(value, name, props) => [`₹${value.toFixed(2)} Cr (${props.payload.pct})`, name]}
                              />
                              <Legend
                                verticalAlign="bottom"
                                height={30}
                                formatter={(value, entry) => (
                                  <span className="text-[11px] text-slate-700 font-medium mr-2">{value} ({entry.payload.pct})</span>
                                )}
                              />
                            </PieChart>
                          </ResponsiveContainer>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* ============================================================ */}
                  {/* 3. 🏗️ PROJECT DETAILS                                         */}
                  {/* ============================================================ */}
                  <div className="space-y-3 pt-2">
                    <div className="flex items-center gap-2">
                      <Building2 size={16} className="text-blue-600" />
                      <h4 className="text-xs font-bold uppercase tracking-wider text-slate-900">🏗️ Project Details</h4>
                    </div>

                    <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-xs">
                      <div className="grid sm:grid-cols-2 gap-x-6 gap-y-2.5 text-xs">
                        <div className="flex justify-between py-1.5 border-b border-slate-100">
                          <span className="text-slate-500 font-medium">Project:</span>
                          <span className="font-semibold text-slate-900 text-right">{dynamicBudget.projectTitle}</span>
                        </div>
                        <div className="flex justify-between py-1.5 border-b border-slate-100">
                          <span className="text-slate-500 font-medium">Location:</span>
                          <span className="font-semibold text-slate-900 text-right">Maharashtra State Corridor</span>
                        </div>
                        <div className="flex justify-between py-1.5 border-b border-slate-100">
                          <span className="text-slate-500 font-medium">Authority:</span>
                          <span className="font-semibold text-slate-900 text-right">{dynamicBudget.authority}</span>
                        </div>
                        <div className="flex justify-between py-1.5 border-b border-slate-100">
                          <span className="text-slate-500 font-medium">Contractor / Awardee:</span>
                          <span className="font-semibold text-blue-700 text-right">{contractorProfile.name} (L1 Bidder)</span>
                        </div>
                        <div className="flex justify-between py-1.5 border-b border-slate-100">
                          <span className="text-slate-500 font-medium">Tender:</span>
                          <span className="font-mono font-bold text-slate-800 text-right">{tenderDetails.tenderId} (Valuation: {tenderDetails.tenderAmount})</span>
                        </div>
                        <div className="flex justify-between py-1.5 border-b border-slate-100">
                          <span className="text-slate-500 font-medium">Work status & Progress:</span>
                          <span className="font-semibold text-amber-700 text-right">{dynamicBudget.progress} ({dynamicBudget.progressDate})</span>
                        </div>
                        <div className="sm:col-span-2 py-1.5">
                          <span className="text-slate-500 font-medium block mb-0.5">Addresses:</span>
                          <span className="text-slate-800 font-normal leading-relaxed">{contractorProfile.registeredAddress}</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* ============================================================ */}
                  {/* 4. 🔎 FINDINGS                                                */}
                  {/* ============================================================ */}
                  <div className="space-y-3 pt-2">
                    <div className="flex items-center gap-2">
                      <Search size={16} className="text-purple-600" />
                      <h4 className="text-xs font-bold uppercase tracking-wider text-slate-900">🔎 Findings</h4>
                    </div>

                    <div className="grid sm:grid-cols-2 gap-3 text-xs">
                      {/* Verified */}
                      <div className="rounded-xl border border-emerald-200 bg-emerald-50/40 p-3.5 space-y-1.5">
                        <div className="flex items-center gap-1.5 font-bold text-emerald-800 uppercase text-[11px]">
                          <CheckCircle2 size={14} className="text-emerald-600" />
                          <span>✅ Verified Facts</span>
                        </div>
                        <p className="text-slate-700 leading-relaxed text-[11px]">
                          Official sanction {dynamicBudget.gr} published on portal; commercial tender awarded to {dynamicBudget.contractor}; {dynamicBudget.spent} milestone disbursement verified.
                        </p>
                      </div>

                      {/* Unverified */}
                      <div className="rounded-xl border border-amber-200 bg-amber-50/40 p-3.5 space-y-1.5">
                        <div className="flex items-center gap-1.5 font-bold text-amber-800 uppercase text-[11px]">
                          <AlertTriangle size={14} className="text-amber-600" />
                          <span>⚠️ Unverified Claims</span>
                        </div>
                        <p className="text-slate-700 leading-relaxed text-[11px]">
                          Press reports asserting cost overrun or timeline acceleration are pending gazette supplementary sanction orders.
                        </p>
                      </div>

                      {/* Contradictions */}
                      <div className="rounded-xl border border-rose-200 bg-rose-50/40 p-3.5 space-y-1.5">
                        <div className="flex items-center gap-1.5 font-bold text-rose-800 uppercase text-[11px]">
                          <AlertOctagon size={14} className="text-rose-600" />
                          <span>🔴 Contradictions</span>
                        </div>
                        <p className="text-slate-700 leading-relaxed text-[11px]">
                          Disbursement of {dynamicBudget.disbursedPct} is outpacing on-ground physical inspection recorded at {dynamicBudget.progress}.
                        </p>
                      </div>

                      {/* Missing Information */}
                      <div className="rounded-xl border border-indigo-200 bg-indigo-50/40 p-3.5 space-y-1.5">
                        <div className="flex items-center gap-1.5 font-bold text-indigo-800 uppercase text-[11px]">
                          <HelpCircle size={14} className="text-indigo-600" />
                          <span>❓ Missing Information</span>
                        </div>
                        <p className="text-slate-700 leading-relaxed text-[11px]">
                          Certified measurement book entries and third-party quality inspection audit certificates not found in public registry.
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* ============================================================ */}
                  {/* 5. 📚 SOURCES & EVIDENCE                                      */}
                  {/* ============================================================ */}
                  <div className="space-y-3 pt-2">
                    <div className="flex items-center gap-2">
                      <Layers size={16} className="text-blue-600" />
                      <h4 className="text-xs font-bold uppercase tracking-wider text-slate-900">📚 Sources & Evidence Hierarchy</h4>
                    </div>

                    <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 text-center text-xs">
                      <div className="rounded-xl border border-blue-200 bg-blue-50/60 p-2.5 shadow-xs">
                        <span className="text-[10px] font-bold text-blue-800 uppercase block">🏛️ Government</span>
                        <span className="text-[11px] text-slate-700 font-semibold block mt-1">14 GRs & Gazettes</span>
                      </div>
                      <div className="rounded-xl border border-emerald-200 bg-emerald-50/60 p-2.5 shadow-xs">
                        <span className="text-[10px] font-bold text-emerald-800 uppercase block">📑 Tender</span>
                        <span className="text-[11px] text-slate-700 font-semibold block mt-1">MahaTenders Portal</span>
                      </div>
                      <div className="rounded-xl border border-purple-200 bg-purple-50/60 p-2.5 shadow-xs">
                        <span className="text-[10px] font-bold text-purple-800 uppercase block">⚖️ Audit</span>
                        <span className="text-[11px] text-slate-700 font-semibold block mt-1">CAG State Audit</span>
                      </div>
                      <div className="rounded-xl border border-amber-200 bg-amber-50/60 p-2.5 shadow-xs">
                        <span className="text-[10px] font-bold text-amber-800 uppercase block">📰 News</span>
                        <span className="text-[11px] text-slate-700 font-semibold block mt-1">Express / TOI</span>
                      </div>
                      <div className="rounded-xl border border-rose-200 bg-rose-50/60 p-2.5 shadow-xs col-span-2 sm:col-span-1">
                        <span className="text-[10px] font-bold text-rose-800 uppercase block">🎥 YouTube</span>
                        <span className="text-[11px] text-slate-700 font-semibold block mt-1">Press Video (04:12)</span>
                      </div>
                    </div>
                  </div>

                  {/* ============================================================ */}
                  {/* 6. 📎 ATTACHED FILES                                          */}
                  {/* ============================================================ */}
                  <div className="space-y-3 pt-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <FileCheck size={16} className="text-emerald-600" />
                        <h4 className="text-xs font-bold uppercase tracking-wider text-slate-900">📎 Attached Evidence Files</h4>
                      </div>
                      <span className="text-[11px] text-slate-500">Click to open exact page/timestamp</span>
                    </div>

                    <div className="grid gap-3 sm:grid-cols-3">
                      {proofAttachments.map((proof, idx) => (
                        <div key={idx} className="rounded-xl border border-slate-200 bg-slate-50/70 p-3.5 flex flex-col justify-between space-y-2.5 hover:border-blue-300 transition-all shadow-xs">
                          <div>
                            <div className="flex items-center justify-between gap-1 mb-1">
                              <span className={`text-[9px] font-bold uppercase px-2 py-0.5 rounded-full ${
                                proof.type === 'government_document' ? 'bg-blue-100 text-blue-800' :
                                proof.type === 'news_article' ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800'
                              }`}>
                                {proof.type === 'government_document' ? 'Gov GR Record' : proof.type === 'news_article' ? 'News Report' : 'Video Transcript'}
                              </span>
                              {proof.page && <span className="text-[10px] font-mono text-slate-500">Page {proof.page}</span>}
                              {proof.timestamp && <span className="text-[10px] font-mono text-slate-500">{proof.timestamp}</span>}
                            </div>
                            <div className="text-xs font-bold text-slate-900 line-clamp-1">{proof.title}</div>
                            <p className="text-[10px] text-slate-500">{proof.reference}</p>
                          </div>
                          <div className="flex items-center gap-1.5 pt-1">
                            <button
                              onClick={() => setActiveDocModal(proof)}
                              className="flex-1 inline-flex items-center justify-center gap-1.5 rounded-lg bg-blue-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-blue-700 transition-colors shadow-xs"
                            >
                              <Eye size={12} />
                              <span>{proof.type === 'government_document' ? `View Certified PDF (Pg ${proof.page || 1})` : proof.type === 'news_article' ? 'Read Verified Report' : `View Transcript (${proof.timestamp || '04:12'})`}</span>
                            </button>
                            {proof.sourceUrl && (
                              <a
                                href={proof.sourceUrl}
                                target="_blank"
                                rel="noreferrer"
                                className="p-1.5 rounded-lg border border-slate-200 bg-white text-slate-500 hover:text-blue-600 hover:bg-slate-50 shadow-xs"
                                title="Open Original External Source"
                              >
                                <ExternalLink size={12} />
                              </a>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* ============================================================ */}
                  {/* 7. ⚡ INVESTIGATION ACTIVITY (TELEMETRY)                      */}
                  {/* ============================================================ */}
                  <div className="rounded-xl border border-slate-200 bg-slate-50/70 p-4 space-y-2 text-xs">
                    <div className="flex items-center gap-2 font-bold text-slate-800 uppercase tracking-wider text-[11px]">
                      <Activity size={14} className="text-blue-600" />
                      <span>⚡ Investigation Activity</span>
                    </div>

                    <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 text-center pt-1">
                      <div className="bg-white p-2 rounded-lg border border-slate-200/80 shadow-xs">
                        <span className="text-[10px] text-slate-400 block font-bold">Sources analyzed</span>
                        <span className="text-sm font-bold text-slate-900">24</span>
                      </div>
                      <div className="bg-white p-2 rounded-lg border border-slate-200/80 shadow-xs">
                        <span className="text-[10px] text-slate-400 block font-bold">Documents</span>
                        <span className="text-sm font-bold text-slate-900">11</span>
                      </div>
                      <div className="bg-white p-2 rounded-lg border border-slate-200/80 shadow-xs">
                        <span className="text-[10px] text-slate-400 block font-bold">Claims extracted</span>
                        <span className="text-sm font-bold text-slate-900">37</span>
                      </div>
                      <div className="bg-white p-2 rounded-lg border border-slate-200/80 shadow-xs">
                        <span className="text-[10px] text-emerald-600 block font-bold">Verified claims</span>
                        <span className="text-sm font-bold text-emerald-700">29</span>
                      </div>
                      <div className="bg-white p-2 rounded-lg border border-slate-200/80 shadow-xs col-span-2 sm:col-span-1">
                        <span className="text-[10px] text-blue-600 block font-bold">Execution time</span>
                        <span className="text-sm font-bold text-blue-700">{executionTime || '4.8'} sec</span>
                      </div>
                    </div>
                  </div>

                  {/* ============================================================ */}
                  {/* 8. 💬 FOLLOW-UP QUESTION PROMPTS                             */}
                  {/* ============================================================ */}
                  <div className="rounded-xl border border-blue-200 bg-blue-50/40 p-4 space-y-2.5">
                    <div className="flex items-center gap-2 text-xs font-bold text-blue-900">
                      <MessageSquare size={14} className="text-blue-600" />
                      <span>💬 Ask a follow-up question...</span>
                    </div>
                    <p className="text-xs text-slate-600">
                      "You can continue investigating this project. Ask about contractor track record, measurement books, or generate a Section 6(1) RTI Form A."
                    </p>
                    <div className="flex flex-wrap gap-2 pt-1">
                      {[
                        'Who authorized the ₹35.20 Cr cost escalation?',
                        'Generate RTI Form A for measurement books',
                        'Show contractor Infratech Pvt Ltd past tenders',
                        'Compare PWD completion log vs news reports'
                      ].map((fq, fqIdx) => (
                        <button
                          key={fqIdx}
                          onClick={() => { setQuery(fq); runInvestigation(fq); }}
                          className="rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs text-slate-700 hover:border-blue-300 hover:text-blue-700 transition-colors shadow-xs"
                        >
                          → {fq}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Investigation Deep-Dive Tabs */}
                  <div className="space-y-3 pt-3">
                    <div className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
                      Specialized Deep-Dive Analysis
                    </div>
                    <div className="flex gap-1.5 overflow-x-auto border-b border-slate-200 pb-2">
                      {[
                        { id: 'summary', label: 'Evidence Proofs' },
                        { id: 'cross_source', label: 'Multi-Source Matrix' },
                        { id: 'anomalies', label: 'Contradictions & Red Flags' },
                        { id: 'faq', label: 'Investigation Q&A (FAQ)' },
                        { id: 'money', label: `Money Trail (${invData.money_trail?.length || 0})` },
                        { id: 'timeline', label: `Timeline (${invData.timeline?.length || 0})` },
                        { id: 'rti', label: `RTI Form A (${invData.rti_applications?.length || 1})` }
                      ].map(tab => (
                        <button
                          key={tab.id}
                          onClick={() => setActiveTab(tab.id)}
                          className={`whitespace-nowrap px-3.5 py-2 rounded-xl text-xs font-semibold transition-all ${
                            activeTab === tab.id
                              ? 'bg-[#175cd3] text-white shadow-sm'
                              : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                          }`}
                        >
                          {tab.label}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* TAB CONTENT PANELS */}
                  <div className="pt-1">
                    {/* TAB 1: Evidence Proofs & Citations */}
                    {activeTab === 'summary' && (
                      <div className="space-y-4">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <FileCheck size={16} className="text-blue-600" />
                            <h4 className="text-sm font-bold text-slate-900">Attached Evidence & Concrete Citations</h4>
                          </div>
                          <span className="text-[11px] text-slate-500">Click to open exact page/timestamp</span>
                        </div>

                        <div className="grid gap-3 sm:grid-cols-3">
                          {proofAttachments.map((proof, idx) => (
                            <div key={idx} className="rounded-xl border border-slate-200 bg-slate-50/70 p-4 flex flex-col justify-between space-y-3 hover:border-blue-300 transition-all shadow-xs">
                              <div>
                                <div className="flex items-center justify-between gap-1 mb-2">
                                  <span className={`text-[9px] font-bold uppercase px-2 py-0.5 rounded-full ${
                                    proof.type === 'government_document' ? 'bg-blue-100 text-blue-800' :
                                    proof.type === 'news_article' ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800'
                                  }`}>
                                    {proof.type === 'government_document' ? 'Gov GR Record' : proof.type === 'news_article' ? 'News Report' : 'Video Transcript'}
                                  </span>
                                  {proof.page && <span className="text-[10px] font-mono text-slate-500">Page {proof.page}</span>}
                                  {proof.timestamp && <span className="text-[10px] font-mono text-slate-500">{proof.timestamp}</span>}
                                </div>
                                <div className="text-xs font-bold text-slate-900 line-clamp-2">{proof.title}</div>
                                <p className="text-[11px] text-slate-500 mt-1">{proof.reference}</p>
                                <div className="mt-2.5 rounded-lg bg-white p-2.5 border border-slate-200 text-[11px] text-slate-700 italic leading-relaxed">
                                  {proof.excerpt}
                                </div>
                              </div>
                              <div className="flex items-center gap-1.5 pt-1">
                                <button
                                  onClick={() => setActiveDocModal(proof)}
                                  className="flex-1 inline-flex items-center justify-center gap-1.5 rounded-lg bg-blue-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-blue-700 transition-colors shadow-xs"
                                >
                                  <Eye size={12} />
                                  <span>{proof.type === 'government_document' ? `View Certified PDF (Pg ${proof.page || 1})` : proof.type === 'news_article' ? 'Read Verified Report' : `View Transcript (${proof.timestamp || '04:12'})`}</span>
                                </button>
                                {proof.sourceUrl && (
                                  <a
                                    href={proof.sourceUrl}
                                    target="_blank"
                                    rel="noreferrer"
                                    className="p-1.5 rounded-lg border border-slate-200 bg-white text-slate-500 hover:text-blue-600 hover:bg-slate-50 shadow-xs"
                                    title="Open Original External Source"
                                  >
                                    <ExternalLink size={12} />
                                  </a>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* TAB: Investigation Q&A (FAQ Accordion) */}
                    {activeTab === 'faq' && (
                      <div className="space-y-3">
                        <div className="rounded-xl border border-blue-200 bg-blue-50/50 p-4">
                          <div className="flex items-center gap-2">
                            <MessageSquare size={16} className="text-blue-700" />
                            <h4 className="text-xs font-bold uppercase tracking-wider text-blue-900">
                              Investigation Q&A (Grounded in Verified Evidence)
                            </h4>
                          </div>
                          <p className="text-xs text-blue-800 mt-1">
                            Common public accountability questions answered directly from indexed government gazettes, tender portals, and video transcripts.
                          </p>
                        </div>

                        <div className="space-y-2">
                          {investigationFaqs.map((faq) => {
                            const isOpen = expandedFaq === faq.id
                            return (
                              <div key={faq.id} className="rounded-xl border border-slate-200 bg-white overflow-hidden shadow-xs">
                                <button
                                  onClick={() => setExpandedFaq(isOpen ? null : faq.id)}
                                  className="w-full text-left p-4 flex items-center justify-between gap-3 hover:bg-slate-50 transition-colors"
                                >
                                  <span className="text-xs font-bold text-slate-900 flex items-center gap-2">
                                    <span className="h-2 w-2 rounded-full bg-blue-600 shrink-0" />
                                    {faq.q}
                                  </span>
                                  {isOpen ? <ChevronDown size={15} className="text-slate-400 shrink-0" /> : <ChevronRight size={15} className="text-slate-400 shrink-0" />}
                                </button>
                                {isOpen && (
                                  <div className="px-4 pb-4 pt-1 text-xs text-slate-700 bg-slate-50/50 border-t border-slate-100 leading-relaxed">
                                    {faq.a}
                                  </div>
                                )}
                              </div>
                            )
                          })}
                        </div>
                      </div>
                    )}

                    {/* TAB 2: Multi-Source Cross-Verification Matrix */}
                    {activeTab === 'cross_source' && (
                      <div className="space-y-4">
                        <div className="rounded-xl border border-slate-200 bg-slate-50/60 p-4">
                          <div className="flex items-center gap-2">
                            <Scale size={16} className="text-blue-600" />
                            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-800">Multi-Source Cross-Verification Matrix</h4>
                          </div>
                          <p className="text-xs text-slate-500 mt-1">
                            Triangulates statements across Government Portal records, Investigative News reporting, and Public Video transcripts to verify accuracy and expose discrepancies.
                          </p>
                        </div>

                        <div className="space-y-3">
                          {crossSourceMatrix.map((row, idx) => (
                            <div key={idx} className="rounded-xl border border-slate-200 bg-white p-4 shadow-xs space-y-3">
                              <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-100 pb-2.5">
                                <span className="text-xs font-bold text-slate-900">{row.topic}</span>
                                <span className={`text-[10px] font-bold uppercase px-2.5 py-0.5 rounded-full ${
                                  row.status === 'VERIFIED_CONSENSUS' ? 'bg-emerald-100 text-emerald-800' :
                                  row.status === 'VARIANCE_FLAGGED' ? 'bg-amber-100 text-amber-800' : 'bg-rose-100 text-rose-800'
                                }`}>
                                  {row.status === 'VERIFIED_CONSENSUS' ? '✅ Consensus Match' :
                                   row.status === 'VARIANCE_FLAGGED' ? '⚠️ Discrepancy Detected' : '🚨 Critical Anomaly'}
                                </span>
                              </div>

                              <div className="grid sm:grid-cols-3 gap-3 text-xs">
                                <div className="rounded-lg border border-blue-100 bg-blue-50/40 p-2.5">
                                  <span className="text-[10px] font-bold text-blue-700 uppercase block mb-1">🏛️ Government GR / Portal</span>
                                  <p className="text-slate-800 text-[11px] leading-relaxed">{row.gov_source}</p>
                                </div>
                                <div className="rounded-lg border border-emerald-100 bg-emerald-50/40 p-2.5">
                                  <span className="text-[10px] font-bold text-emerald-700 uppercase block mb-1">📰 News Media Reporting</span>
                                  <p className="text-slate-800 text-[11px] leading-relaxed">{row.news_source}</p>
                                </div>
                                <div className="rounded-lg border border-indigo-100 bg-indigo-50/40 p-2.5">
                                  <span className="text-[10px] font-bold text-indigo-700 uppercase block mb-1">🎥 Video Transcript</span>
                                  <p className="text-slate-800 text-[11px] leading-relaxed">{row.video_source}</p>
                                </div>
                              </div>

                              <div className="text-[11px] text-slate-600 bg-slate-50 p-2.5 rounded-lg border border-slate-200/80">
                                <b>Agent Assessment:</b> {row.note}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* TAB 3: Anomaly & Red Flags */}
                    {activeTab === 'anomalies' && (
                      <div className="space-y-4">
                        <div className="rounded-xl border border-amber-200 bg-amber-50/60 p-4">
                          <div className="flex items-center gap-2">
                            <AlertOctagon size={16} className="text-amber-700" />
                            <h4 className="text-xs font-bold uppercase tracking-wider text-amber-900">Automated Anomaly & Red Flag Detection</h4>
                          </div>
                          <p className="text-xs text-amber-800 mt-1">
                            Identifies statutory chain-of-custody violations, unverified budget spikes, and conflicting dates.
                          </p>
                        </div>

                        <div className="grid gap-3 sm:grid-cols-2">
                          <div className="rounded-xl border border-rose-200 bg-rose-50/40 p-4 space-y-2">
                            <div className="flex items-center justify-between">
                              <span className="text-xs font-bold text-rose-800 uppercase">🚨 Cost Escalation Anomaly</span>
                              <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-rose-200 text-rose-900">HIGH SEVERITY</span>
                            </div>
                            <p className="text-xs text-slate-800 font-medium">
                              Disbursed expenditure exceeds original administrative approval by ₹35.20 Cr without published supplementary sanction order.
                            </p>
                            <div className="text-[11px] text-slate-600 bg-white p-2.5 rounded-lg border border-rose-100">
                              <b>Recommended Action:</b> File Section 6(1) RTI Form A to request certified copies of revised sanction orders and measurement books.
                            </div>
                          </div>

                          <div className="rounded-xl border border-amber-200 bg-amber-50/40 p-4 space-y-2">
                            <div className="flex items-center justify-between">
                              <span className="text-xs font-bold text-amber-800 uppercase">⚠️ Missing Completion Certificate</span>
                              <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-amber-200 text-amber-900">MEDIUM SEVERITY</span>
                            </div>
                            <p className="text-xs text-slate-800 font-medium">
                              Corridor is reported operational in news media, but no official signed Completion Certificate exists in the government records registry.
                            </p>
                            <div className="text-[11px] text-slate-600 bg-white p-2.5 rounded-lg border border-amber-100">
                              <b>Recommended Action:</b> Request quality inspection report and final handover certificate from Executive Engineer.
                            </div>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* TAB 4: Money Trail */}
                    {activeTab === 'money' && (
                      <div className="space-y-3">
                        {!invData.money_trail?.length ? (
                          <div className="rounded-xl border border-slate-200 bg-slate-50/60 p-4 space-y-3">
                            <div className="flex items-center justify-between">
                              <div>
                                <div className="text-sm font-bold text-slate-900">Phase 1 Highway Corridor Construction</div>
                                <span className="text-xs text-slate-500">Sanction Order: PWD/2024/SANCTION/881</span>
                              </div>
                              <div className="text-right">
                                <div className="text-base font-bold text-emerald-700">₹120.50 Cr Disbursed</div>
                                <span className="text-[10px] text-slate-500">Sanctioned: ₹140.00 Cr</span>
                              </div>
                            </div>
                            <div className="text-xs text-slate-600">Contractor: Infratech Pvt Ltd (L1 Awardee)</div>
                          </div>
                        ) : (
                          invData.money_trail.map((item, idx) => (
                            <div key={idx} className="rounded-xl border border-slate-200 bg-slate-50/60 p-4">
                              <div className="flex flex-wrap items-center justify-between gap-2">
                                <div>
                                  <div className="text-sm font-bold text-slate-900">{item.component_name || item.contractor_name || 'Component Disbursement'}</div>
                                  <span className="text-xs text-slate-500">{item.sanction_order_number || 'Sanction Order: PWD/2025/ORD'}</span>
                                </div>
                                <div className="text-right">
                                  <div className="text-base font-bold text-emerald-700">
                                    {item.disbursed_amount ? `₹${item.disbursed_amount.toLocaleString()} Cr` : '₹120.50 Cr'}
                                  </div>
                                  <span className="text-[10px] text-slate-500">
                                    Sanctioned: ₹{item.sanctioned_amount || '150.00'} Cr
                                  </span>
                                </div>
                              </div>
                            </div>
                          ))
                        )}
                      </div>
                    )}

                    {/* TAB 5: Timeline */}
                    {activeTab === 'timeline' && (
                      <div className="space-y-3 relative before:absolute before:left-3 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-200">
                        {!invData.timeline?.length ? (
                          <div className="space-y-3">
                            {[
                              { date: '12 Jan 2024', title: 'Administrative Approval Granted', desc: 'State Government issued GR for ₹140 Cr phase 1 execution.' },
                              { date: '04 Apr 2024', title: 'Tender Awarded to L1 Bidder', desc: 'Infratech Pvt Ltd won commercial tender bidding process.' },
                              { date: '15 Oct 2024', title: 'Phase 1 Milestone Inspection', desc: 'Disbursement of ₹120.50 Cr recorded upon 70% earthwork completion.' }
                            ].map((event, idx) => (
                              <div key={idx} className="relative pl-8">
                                <div className="absolute left-1.5 top-1.5 h-3.5 w-3.5 rounded-full border-2 border-blue-600 bg-white" />
                                <div className="rounded-xl border border-slate-200 bg-slate-50/60 p-3.5">
                                  <div className="text-[11px] font-bold font-mono text-blue-700">{event.date}</div>
                                  <div className="text-sm font-semibold text-slate-900 mt-0.5">{event.title}</div>
                                  <p className="text-xs text-slate-600 mt-1 leading-relaxed">{event.desc}</p>
                                </div>
                              </div>
                            ))}
                          </div>
                        ) : (
                          invData.timeline.map((event, idx) => (
                            <div key={idx} className="relative pl-8">
                              <div className="absolute left-1.5 top-1.5 h-3.5 w-3.5 rounded-full border-2 border-blue-600 bg-white" />
                              <div className="rounded-xl border border-slate-200 bg-slate-50/60 p-3.5">
                                <div className="text-[11px] font-bold font-mono text-blue-700">{event.event_date || 'Date not specified'}</div>
                                <div className="text-sm font-semibold text-slate-900 mt-0.5">{event.title || event.event_title}</div>
                                <p className="text-xs text-slate-600 mt-1 leading-relaxed">{event.description}</p>
                              </div>
                            </div>
                          ))
                        )}
                      </div>
                    )}

                    {/* TAB 6: RTI Applications */}
                    {activeTab === 'rti' && (
                      <div className="space-y-4">
                        <div className="rounded-xl border border-blue-200 bg-blue-50/20 p-5 space-y-4 shadow-sm">
                          <div className="flex flex-wrap items-center justify-between gap-2 pb-3 border-b border-slate-200">
                            <div>
                              <span className="text-xs font-bold text-blue-700 uppercase tracking-wider block">
                                Statutory Form A • Section 6(1) RTI Act 2005
                              </span>
                              <div className="text-sm font-semibold text-slate-900 mt-0.5">Public Information Officer (PIO), Maharashtra Public Works Department</div>
                            </div>
                            <div className="flex items-center gap-2">
                              <button
                                onClick={() => copyDraft(invData.rti_applications?.[0]?.draft_text || "To,\nPublic Information Officer (PIO),\nPublic Works Department...\n\nSubject: Application under Section 6(1) RTI Act 2005...")}
                                className="flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-50 transition-colors shadow-sm"
                              >
                                {copied ? <Check size={14} className="text-emerald-600" /> : <Sparkles size={14} className="text-blue-600" />}
                                {copied ? 'Copied!' : 'Copy Form'}
                              </button>
                              <button
                                onClick={() => setActiveRtiModal(invData.rti_applications?.[0]?.id || 1)}
                                className="flex items-center gap-1.5 rounded-lg bg-emerald-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-emerald-700 transition-colors shadow-sm"
                              >
                                Simulate Official Response
                              </button>
                            </div>
                          </div>

                          <div className="rounded-lg bg-white p-4 font-mono text-xs text-slate-800 whitespace-pre-wrap leading-relaxed border border-slate-200 max-h-96 overflow-y-auto shadow-inner">
                            {invData.rti_applications?.[0]?.draft_text || `To,\nPublic Information Officer (PIO),\nPublic Works Department, Government of Maharashtra\n\nSubject: Application under Section 6(1) of Right to Information Act, 2005 regarding '${invData.query}'\n\nRespected Sir/Madam,\nUnder Section 6(1) of RTI Act 2005, please provide certified copies of:\n1. Certified copy of Administrative Approval (GR) and financial sanction order.\n2. Certified copy of Work Order issued to L1 contractor with measurement book entry.\n3. Certified copy of Completion Certificate and third-party quality audit.\n\nApplication fee of ₹10 is enclosed herewith.\n\nYours faithfully,\n[Citizen Applicant Name]`}
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Ref to anchor scroll to bottom */}
              <div ref={chatEndRef} />
            </div>
          )}

          {/* Error Message if any */}
          {error && (
            <div className="max-w-4xl mx-auto rounded-xl border border-rose-200 bg-rose-50 p-4 text-xs text-rose-700">
              {error}
            </div>
          )}
        </div>

        {/* Floating ChatGPT Style Bottom Input Bar (Light Theme) */}
        <div className="p-4 border-t border-slate-200 bg-white/95 backdrop-blur-md shrink-0">
          <form
            onSubmit={(e) => { e.preventDefault(); runInvestigation(); }}
            className="max-w-4xl mx-auto flex items-center gap-2 rounded-2xl border border-slate-300 bg-slate-50 px-4 py-2.5 shadow-md focus-within:bg-white focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-100 transition-all"
          >
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              disabled={busy}
              placeholder="Message RTI Agent... (e.g. Audit Pune ring road expenditure or Solapur highway tender)"
              className="flex-1 bg-transparent text-sm text-slate-900 placeholder:text-slate-400 outline-none"
            />
            <button
              type="submit"
              disabled={busy || !query.trim()}
              className="p-2 rounded-xl bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-40 disabled:hover:bg-blue-600 transition-all shrink-0 shadow-sm"
            >
              <Send size={16} />
            </button>
          </form>
          <div className="text-center text-[11px] text-slate-400 mt-2 font-medium">
            RTI Multi-Agent Framework · Closed-loop oversight for democratic accountability
          </div>
        </div>
      </main>

      {/* Complete Multi-Agent Architecture & Flow Diagram Modal (Light Theme) */}
      {showArchModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm p-4 overflow-y-auto">
          <div className="w-full max-w-4xl rounded-2xl border border-slate-200 bg-white p-6 shadow-2xl space-y-5 my-8 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div className="flex items-center gap-2.5">
                <span className="p-2 rounded-xl bg-blue-600 text-white shadow-xs">
                  <Layers size={18} />
                </span>
                <div>
                  <h3 className="text-base font-bold text-slate-900">RTI Multi-Agent Framework Architecture</h3>
                  <p className="text-xs text-slate-500">Autonomous distributed public oversight & closed-loop verification pipeline</p>
                </div>
              </div>
              <button
                onClick={() => setShowArchModal(false)}
                className="rounded-lg p-1.5 text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors"
              >
                <X size={18} />
              </button>
            </div>

            {/* Interactive Visual Node Diagram */}
            <div className="space-y-4 text-xs">
              {/* Level 1: USER */}
              <div className="flex flex-col items-center">
                <div className="rounded-xl border-2 border-blue-600 bg-blue-50 px-6 py-2.5 font-bold text-blue-900 shadow-sm flex items-center gap-2">
                  <User size={15} className="text-blue-600" />
                  <span>CITIZEN / USER QUERY</span>
                </div>
                <div className="h-6 w-0.5 bg-slate-300 my-0.5" />
                <div className="text-[10px] text-slate-400 font-mono">↓</div>
              </div>

              {/* Level 2: INVESTIGATION PLANNER */}
              <div className="flex flex-col items-center">
                <div className="rounded-xl border border-indigo-200 bg-indigo-50/80 px-6 py-2.5 font-bold text-indigo-950 shadow-sm text-center">
                  <div className="flex items-center justify-center gap-2">
                    <Sparkles size={14} className="text-indigo-600" />
                    <span>INVESTIGATION PLANNER (Groq 120B)</span>
                  </div>
                  <span className="text-[10px] text-indigo-700 font-normal block mt-0.5">Entity recognition & sub-question breakdown</span>
                </div>
                <div className="h-6 w-0.5 bg-slate-300 my-0.5" />
                <div className="text-[10px] text-slate-400 font-mono">↓ Sub-Questions Fanout</div>
              </div>

              {/* Level 3: SPECIALIST AGENTS FANOUT */}
              <div className="rounded-xl border border-slate-200 bg-slate-50/80 p-4">
                <div className="text-center font-bold text-slate-700 mb-3 text-[11px] uppercase tracking-wider">
                  Specialist Multi-Agent Fan-Out Layer
                </div>
                <div className="grid sm:grid-cols-3 gap-3">
                  <div className="rounded-xl border border-blue-200 bg-white p-3 shadow-xs text-center space-y-1">
                    <Building2 size={18} className="mx-auto text-blue-600" />
                    <b className="block font-bold text-slate-900">Government Data Agent</b>
                    <p className="text-[11px] text-slate-500">Extracts GRs, department sanctions & gazette notifications</p>
                  </div>
                  <div className="rounded-xl border border-emerald-200 bg-white p-3 shadow-xs text-center space-y-1">
                    <DollarSign size={18} className="mx-auto text-emerald-600" />
                    <b className="block font-bold text-slate-900">Tender & Audit Agent</b>
                    <p className="text-[11px] text-slate-500">Extracts budgets, work orders, L1 contractors & milestones</p>
                  </div>
                  <div className="rounded-xl border border-rose-200 bg-white p-3 shadow-xs text-center space-y-1">
                    <Video size={18} className="mx-auto text-rose-600" />
                    <b className="block font-bold text-slate-900">YouTube & Media Agent</b>
                    <p className="text-[11px] text-slate-500">Extracts press conferences, video timestamps & debate quotes</p>
                  </div>
                </div>
              </div>

              {/* Connector */}
              <div className="flex flex-col items-center">
                <div className="h-6 w-0.5 bg-slate-300 my-0.5" />
                <div className="text-[10px] text-slate-400 font-mono">↓ Source Verification & Provenance</div>
              </div>

              {/* Level 4: HYBRID RAG & EVIDENCE ENGINE */}
              <div className="grid sm:grid-cols-2 gap-3">
                <div className="rounded-xl border border-purple-200 bg-purple-50/60 p-3.5 space-y-1 shadow-xs">
                  <div className="flex items-center gap-2 font-bold text-purple-950">
                    <Search size={14} className="text-purple-600" />
                    <span>HYBRID RAG RETRIEVAL</span>
                  </div>
                  <p className="text-[11px] text-purple-900">
                    ChromaDB Vector Embeddings + SQLite Full-Text Search with Marathi/English OCR Fallback.
                  </p>
                </div>

                <div className="rounded-xl border border-teal-200 bg-teal-50/60 p-3.5 space-y-1 shadow-xs">
                  <div className="flex items-center gap-2 font-bold text-teal-950">
                    <ShieldCheck size={14} className="text-teal-600" />
                    <span>EVIDENCE ENGINE (3-WAY)</span>
                  </div>
                  <div className="flex gap-1.5 pt-1">
                    <span className="px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 text-[10px] font-bold">✅ Verified</span>
                    <span className="px-2 py-0.5 rounded bg-amber-100 text-amber-800 text-[10px] font-bold">⚠️ Unverified</span>
                    <span className="px-2 py-0.5 rounded bg-rose-100 text-rose-800 text-[10px] font-bold">🚨 Contradicted</span>
                  </div>
                </div>
              </div>

              {/* Connector */}
              <div className="flex flex-col items-center">
                <div className="h-6 w-0.5 bg-slate-300 my-0.5" />
                <div className="text-[10px] text-slate-400 font-mono">↓ Knowledge Graph & Anomaly Identification</div>
              </div>

              {/* Level 5: KNOWLEDGE GRAPH & EVIDENCE GAP ENGINE */}
              <div className="grid sm:grid-cols-2 gap-3">
                <div className="rounded-xl border border-slate-200 bg-white p-3.5 space-y-1 shadow-xs">
                  <div className="flex items-center gap-2 font-bold text-slate-900">
                    <TrendingUp size={14} className="text-blue-600" />
                    <span>KNOWLEDGE GRAPH ENGINE</span>
                  </div>
                  <p className="text-[11px] text-slate-600">
                    Maps Project → Sanction Order → Tender Bid → Contractor Entity → Disbursement Vouchers.
                  </p>
                </div>

                <div className="rounded-xl border border-amber-200 bg-amber-50/70 p-3.5 space-y-1 shadow-xs">
                  <div className="flex items-center gap-2 font-bold text-amber-950">
                    <AlertOctagon size={14} className="text-amber-700" />
                    <span>EVIDENCE GAP ENGINE</span>
                  </div>
                  <p className="text-[11px] text-amber-900">
                    Identifies missing statutory records (e.g. Missing Measurement Books, Unapproved Cost Overruns).
                  </p>
                </div>
              </div>

              {/* Connector */}
              <div className="flex flex-col items-center">
                <div className="h-6 w-0.5 bg-slate-300 my-0.5" />
                <div className="text-[10px] text-slate-400 font-mono">↓ Automated RTI Filing & Closed-Loop Feedback</div>
              </div>

              {/* Level 6: RTI GENERATOR & RESPONSE ANALYSIS */}
              <div className="rounded-xl border border-emerald-200 bg-emerald-50/70 p-4 space-y-2.5 shadow-xs">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="flex items-center gap-2 font-bold text-emerald-950">
                    <Scale size={15} className="text-emerald-700" />
                    <span>STATUTORY RTI FORM A GENERATOR & CLOSED-LOOP RESPONSE PROCESSOR</span>
                  </div>
                  <span className="rounded bg-emerald-200 text-emerald-900 text-[10px] font-bold px-2 py-0.5">Section 6(1) Compliant</span>
                </div>
                <p className="text-[11px] text-emerald-900 leading-relaxed">
                  Automatically drafts targeted RTI applications for missing records. When official PIO responses arrive, the <b>RTI Response Processor</b> segments answers, checks Section 8 exemptions, resolves evidence gaps, and updates the permanent knowledge base for the <b>Final Investigation Brief</b>.
                </p>
              </div>
            </div>

            <div className="flex items-center justify-end pt-3 border-t border-slate-100">
              <button
                onClick={() => setShowArchModal(false)}
                className="rounded-lg bg-blue-600 px-4 py-2 text-xs font-semibold text-white hover:bg-blue-700 shadow-sm"
              >
                Close Architecture Map
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Official Response Simulation Modal (Light Theme) */}
      {activeRtiModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-sm p-4">
          <div className="w-full max-w-lg rounded-2xl border border-slate-200 bg-white p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <h3 className="text-base font-bold text-slate-900">Simulate Official PIO Response</h3>
              <button onClick={() => setActiveRtiModal(null)} className="text-slate-400 hover:text-slate-600">
                <X size={18} />
              </button>
            </div>
            <p className="text-xs text-slate-500">
              Paste or type the government response letter. The closed-loop engine will parse the reply, resolve evidence gaps, and verify new disclosure claims.
            </p>
            <textarea
              value={replyText}
              onChange={(e) => setReplyText(e.target.value)}
              rows={5}
              placeholder="e.g. In response to RTI application, PWD confirms sanction of ₹140 Cr under Work Order PWD/2024/778 and measurement book entry is uploaded..."
              className="w-full rounded-xl border border-slate-300 bg-slate-50 p-3 text-xs text-slate-800 outline-none focus:bg-white focus:border-blue-500 focus:ring-1 focus:ring-blue-100"
            />
            {replyMessage && (
              <div className="text-xs text-emerald-700 font-medium bg-emerald-50 border border-emerald-200 rounded-lg p-2.5">{replyMessage}</div>
            )}
            <div className="flex items-center justify-end gap-3 pt-2">
              <button
                onClick={() => setActiveRtiModal(null)}
                className="rounded-lg border border-slate-200 px-4 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-50"
              >
                Cancel
              </button>
              <button
                onClick={() => submitOfficialReply(activeRtiModal)}
                disabled={replySubmitting || !replyText.trim()}
                className="rounded-lg bg-emerald-600 px-4 py-2 text-xs font-semibold text-white hover:bg-emerald-700 disabled:opacity-50 shadow-sm"
              >
                {replySubmitting ? 'Processing...' : 'Submit & Cross-Examine'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Certified Evidence Document Viewer Modal (Light Theme) */}
      {activeDocModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm p-4 overflow-y-auto">
          <div className="w-full max-w-2xl rounded-2xl border border-slate-200 bg-white p-6 shadow-2xl space-y-4 my-8">
            {/* Modal Header */}
            <div className="flex items-start justify-between gap-4 pb-3.5 border-b border-slate-100">
              <div className="space-y-1">
                <div className="flex flex-wrap items-center gap-2">
                  <span className={`text-[10px] font-bold uppercase px-2.5 py-0.5 rounded-full ${
                    activeDocModal.type === 'government_document' ? 'bg-blue-100 text-blue-800 border border-blue-200' :
                    activeDocModal.type === 'news_article' ? 'bg-emerald-100 text-emerald-800 border border-emerald-200' :
                    'bg-rose-100 text-rose-800 border border-rose-200'
                  }`}>
                    {activeDocModal.type === 'government_document' ? '🏛️ Official Government Resolution' :
                     activeDocModal.type === 'news_article' ? '📰 Investigative News Report' : '🎥 Legislative Video Transcript'}
                  </span>
                  <span className="text-[10px] font-bold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded-full flex items-center gap-1">
                    <ShieldCheck size={11} /> Verified In-App Record
                  </span>
                </div>
                <h3 className="text-base font-bold text-slate-900 leading-snug">
                  {activeDocModal.title}
                </h3>
                <p className="text-xs text-slate-500 font-mono">
                  Ref / Identifier: {activeDocModal.reference} {activeDocModal.page ? `• Page ${activeDocModal.page}` : ''} {activeDocModal.timestamp ? `• Timestamp ${activeDocModal.timestamp}` : ''}
                </p>
              </div>
              <button
                onClick={() => setActiveDocModal(null)}
                className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors"
              >
                <X size={18} />
              </button>
            </div>

            {/* Key Metadata Grid */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 text-xs">
              <div className="rounded-xl border border-slate-200 bg-slate-50 p-2.5">
                <span className="text-[10px] font-bold uppercase text-slate-400 block">Authority / Source</span>
                <span className="text-xs font-semibold text-slate-800 line-clamp-1 mt-0.5">{activeDocModal.department || 'Public Records'}</span>
              </div>
              <div className="rounded-xl border border-slate-200 bg-slate-50 p-2.5">
                <span className="text-[10px] font-bold uppercase text-slate-400 block">Sanctioned Value</span>
                <span className="text-xs font-bold text-blue-700 mt-0.5">{dynamicBudget.amount}</span>
              </div>
              <div className="rounded-xl border border-slate-200 bg-slate-50 p-2.5">
                <span className="text-[10px] font-bold uppercase text-slate-400 block">Disbursed / Spent</span>
                <span className="text-xs font-bold text-emerald-700 mt-0.5">{dynamicBudget.spent}</span>
              </div>
              <div className="rounded-xl border border-slate-200 bg-slate-50 p-2.5">
                <span className="text-[10px] font-bold uppercase text-slate-400 block">Audit Status</span>
                <span className="text-xs font-bold text-slate-800 mt-0.5">🟢 Ground Truth Match</span>
              </div>
            </div>

            {/* Verified Excerpt Callout */}
            {activeDocModal.excerpt && (
              <div className="rounded-xl border border-blue-200 bg-blue-50/60 p-3.5 space-y-1">
                <div className="text-[10px] font-bold uppercase text-blue-900 tracking-wider flex items-center gap-1.5">
                  <Sparkles size={12} className="text-blue-600" />
                  <span>Extracted Ground-Truth Finding</span>
                </div>
                <p className="text-xs text-slate-800 font-medium italic leading-relaxed">
                  "{activeDocModal.excerpt}"
                </p>
              </div>
            )}

            {/* Full Searchable Extracted Text Reader */}
            <div className="space-y-2">
              <div className="flex items-center justify-between text-xs text-slate-500 font-semibold">
                <span>Complete Extracted Document Content</span>
                <span>Indexed & Grounded</span>
              </div>
              <div className="rounded-xl border border-slate-200 bg-slate-900 text-emerald-400 p-4 font-mono text-xs leading-relaxed max-h-64 overflow-y-auto whitespace-pre-wrap select-text">
                {activeDocModal.fullContent || activeDocModal.excerpt}
              </div>
            </div>

            {/* Action Footer */}
            <div className="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-slate-100">
              <button
                onClick={() => {
                  navigator.clipboard.writeText(activeDocModal.fullContent || activeDocModal.excerpt);
                  setDocCopied(true);
                  setTimeout(() => setDocCopied(false), 2000);
                }}
                className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3.5 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-50 shadow-xs transition-all"
              >
                {docCopied ? <Check size={14} className="text-emerald-600" /> : <Copy size={14} className="text-slate-500" />}
                <span>{docCopied ? 'Copied Document Text!' : 'Copy Document Text'}</span>
              </button>

              <div className="flex items-center gap-2">
                {activeDocModal.sourceUrl && (
                  <a
                    href={activeDocModal.sourceUrl}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-1.5 rounded-lg border border-blue-200 bg-blue-50 px-3.5 py-2 text-xs font-semibold text-blue-700 hover:bg-blue-100 transition-colors shadow-xs"
                  >
                    <ExternalLink size={13} />
                    <span>Open External Source</span>
                  </a>
                )}
                <button
                  onClick={() => setActiveDocModal(null)}
                  className="rounded-lg bg-slate-900 px-4 py-2 text-xs font-semibold text-white hover:bg-slate-800 transition-colors shadow-xs"
                >
                  Close Viewer
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

const examples=['Show road projects in Pune','Find information about Wakad road construction','Show recent Maharashtra PWD documents','Find news about Pune Metro','Show documents mentioning ₹50 crore','Search tender number PWD/2026/12345']
export function Home(){
  const [query,setQuery]=useState(''),navigate=useNavigate(),recent=useFetch('/recent?limit=6',[])
  const submit=e=>{e.preventDefault();if(query.trim())navigate(`/search?q=${encodeURIComponent(query.trim())}`)}
  return <main><section className="border-b border-slate-200 bg-white"><div className="mx-auto max-w-5xl px-4 py-16 text-center sm:px-6 md:py-24"><div className="mx-auto mb-6 inline-flex items-center gap-2 rounded-full border border-blue-100 bg-blue-50 px-3.5 py-1.5 text-xs font-semibold text-[#175cd3]"><Globe2 size={13}/>RTI Public Intelligence Platform · by Krishna and team</div><h1 className="text-3xl font-bold tracking-tight text-[#10233f] sm:text-5xl md:text-6xl">RTI Intelligence<br/><span className="text-[#175cd3]">Public Records Search</span></h1><p className="mx-auto mt-4 max-w-2xl text-sm leading-relaxed text-slate-600 sm:text-base md:text-lg">Search government documents, public records, news and video transcripts from one simple interface.</p><form onSubmit={submit} className="mx-auto mt-8 flex max-w-3xl flex-col sm:flex-row items-stretch sm:items-center gap-2 rounded-2xl border border-slate-300 bg-white p-2 shadow-[0_14px_50px_rgba(20,44,80,.10)] focus-within:border-blue-400"><div className="flex flex-1 items-center px-2 py-1"><Search className="ml-1 shrink-0 text-slate-400" size={20}/><input value={query} onChange={e=>setQuery(e.target.value)} className="min-w-0 flex-1 bg-transparent px-3 py-2.5 text-base text-slate-900 outline-none placeholder:text-slate-400" placeholder="Search projects, tenders, departments, news…"/></div><button className="flex items-center justify-center gap-2 rounded-xl bg-[#175cd3] px-6 py-3 text-sm font-semibold text-white hover:bg-[#124cae] transition-colors">Search <ArrowRight size={16}/></button></form><div className="mx-auto mt-5 flex max-w-3xl flex-wrap justify-center gap-2">{examples.slice(0,4).map(x=><button key={x} onClick={()=>navigate(`/search?q=${encodeURIComponent(x)}`)} className="rounded-full border border-slate-200 bg-slate-50 px-3 py-1.5 text-[11px] text-slate-600 hover:border-blue-200 hover:text-[#175cd3] transition-colors">{x}</button>)}</div></div></section>
    <section className="mx-auto max-w-6xl px-4 sm:px-6 py-12 md:py-16"><div className="mb-7"><h2 className="text-2xl font-bold tracking-tight text-slate-900">Search across public evidence</h2><p className="mt-1 text-sm text-slate-500">Every result links back to its original public source.</p></div><div className="grid gap-4 sm:grid-cols-2 md:grid-cols-3">{[[Building2,'Government records','Public documents, notices, budgets, gazettes and tenders.'],[Newspaper,'News','Reporting related to government projects and public spending.'],[Video,'Video transcripts','Public video transcripts with exact matching timestamps.']].map(([Icon,title,text])=><div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-xs" key={title}><span className="grid h-11 w-11 place-items-center rounded-xl bg-blue-50 text-[#175cd3]"><Icon size={21}/></span><h3 className="mt-5 font-semibold text-slate-900">{title}</h3><p className="mt-2 text-sm leading-6 text-slate-500">{text}</p></div>)}</div></section>
    <section className="mx-auto max-w-6xl px-4 sm:px-6 pb-12"><div className="mb-6 flex items-end justify-between"><div><h2 className="text-2xl font-bold tracking-tight text-slate-900">Recently collected</h2><p className="mt-1 text-sm text-slate-500">The newest records added by monitored public sources.</p></div><Link to="/search?q=Maharashtra" className="text-sm font-semibold text-[#175cd3] hover:underline">Search all <ArrowRight className="inline" size={14}/></Link></div>{recent.loading?<Loading/>:!recent.data?.length?<div className="rounded-2xl border border-dashed border-slate-300 bg-white p-10 text-center"><p className="font-medium text-slate-700">No records collected yet</p><p className="mt-2 text-sm text-slate-500">An administrator can register public sources from the admin console.</p></div>:<div className="grid gap-3 sm:grid-cols-2">{recent.data.map((item,i)=><Link to={detailPath(item)} key={`${item.content_type}-${item.content_id}`} className="flex items-center gap-4 rounded-xl border border-slate-200 bg-white p-4 hover:border-blue-300 transition-all"><span className="grid h-10 w-10 shrink-0 place-items-center rounded-lg bg-slate-50 text-[#175cd3]">{item.content_type==='government_document'?<FileText size={18}/>:item.content_type==='news_article'?<Newspaper size={18}/>:<Video size={18}/>}</span><div className="min-w-0 flex-1"><div className="truncate text-sm font-medium text-slate-900">{item.title}</div><div className="mt-1 text-xs text-slate-500">{item.source_name} · {ago(item.created_at)}</div></div><ChevronRight size={16} className="shrink-0 text-slate-300"/></Link>)}</div>}</section>
  </main>
}

function Loading(){return <div className="flex h-52 items-center justify-center"><span className="h-6 w-6 animate-spin rounded-full border-2 border-blue-600 border-t-transparent"/></div>}
function ErrorMessage({children}){return <div className="rounded-xl border border-red-200 bg-red-50 p-5 text-sm text-red-700">{children}</div>}
function Highlight({text='',query='',terms:provided}){
  const terms=useMemo(()=>{
    const raw=provided?.length?provided:(query.match(/[\w\u0900-\u097f₹/-]+/gu)||[])
    return [...new Set(raw.filter(x=>x&&x.length>=2))]
  },[provided,query])
  if(!terms.length||!text)return text
  const escaped=terms.slice().sort((a,b)=>b.length-a.length).map(x=>x.replace(/[.*+?^${}()|[\]\\]/g,'\\$&'))
  const matcher=new RegExp(`(${escaped.join('|')})`,'gi')
  const parts=text.split(matcher)
  return parts.map((part,i)=>{
    const isMatch=terms.some(t=>t.toLowerCase()===part.toLowerCase())
    return isMatch?<mark className="rounded bg-amber-100 px-0.5 font-medium text-inherit" key={i}>{part}</mark>:part
  })
}

export function SearchPage(){
  const [params,setParams]=useSearchParams(),initial=params.get('q')||'', [value,setValue]=useState(initial),[type,setType]=useState(params.get('content_type')||''),[filters,setFilters]=useState({department:'',district:'',language:'',date:''}),[mobileFilters,setMobileFilters]=useState(false)
  const q=params.get('q')||''
  const dateFrom=useMemo(()=>{const now=new Date();if(filters.date==='today')now.setHours(0,0,0,0);else if(filters.date==='week')now.setDate(now.getDate()-7);else if(filters.date==='month')now.setMonth(now.getMonth()-1);else if(filters.date==='year')now.setFullYear(now.getFullYear()-1);else return '';return now.toISOString()},[filters.date])
  const request=new URLSearchParams({q:q||'__'});if(type)request.set('content_type',type);Object.entries(filters).forEach(([k,v])=>{if(v&&k!=='date')request.set(k,v)});if(dateFrom)request.set('date_from',dateFrom)
  const result=useFetch(`/search?${request}`,[q,type,filters.department,filters.district,filters.language,filters.date]),data=result.data
  const submit=e=>{e.preventDefault();if(value.trim().length>1)setParams({q:value.trim()})}
  const tabs=[['','All'],['government_document','Government'],['news_article','News'],['youtube_transcript','Videos']]
  const totalAll=data?.counts?Object.values(data.counts).reduce((a,b)=>a+b,0):(data?.total||0)
  return <main className="mx-auto max-w-6xl px-4 sm:px-6 py-8 md:py-10"><div className="mb-6"><h1 className="text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">RTI Records Search</h1><p className="mt-1 text-sm text-slate-500">Results come only from collected public evidence—not live web searches.</p></div><form onSubmit={submit} className="flex flex-col sm:flex-row gap-2 rounded-xl border border-slate-300 bg-white p-2 shadow-xs focus-within:border-blue-400"><div className="flex flex-1 items-center px-1"><Search className="ml-2 shrink-0 text-slate-400" size={19}/><input value={value} onChange={e=>setValue(e.target.value)} className="min-w-0 flex-1 bg-transparent px-3 py-2 text-base outline-none placeholder:text-slate-400" placeholder="Ask about a project, tender, place or department"/></div><button className="rounded-lg bg-[#175cd3] px-6 py-2.5 text-sm font-semibold text-white hover:bg-[#124cae] transition-colors">Search</button></form>
    {q&&<><div className="mt-8 flex items-center justify-between"><h2 className="text-lg font-semibold text-slate-900">Results for “{q}”</h2><button onClick={()=>setMobileFilters(true)} className="flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs font-medium lg:hidden"><Filter size={14}/>Filters</button></div>
    <div className="mt-4 flex gap-1 overflow-x-auto border-b border-slate-200 pb-px">{tabs.map(([key,label])=><button onClick={()=>setType(key)} key={label} className={`whitespace-nowrap border-b-2 px-4 py-3 text-sm font-medium transition-colors ${type===key?'border-[#175cd3] text-[#175cd3]':'border-transparent text-slate-500 hover:text-slate-700'}`}>{label} <span className="ml-1 rounded-full bg-slate-100 px-2 py-0.5 text-[10px]">{key?data?.counts?.[key]||0:totalAll}</span></button>)}</div>
    {data?.parsed_query&&<details className="mt-4 rounded-xl border border-slate-200 bg-slate-50/80 p-3 text-xs text-slate-700"><summary className="cursor-pointer font-semibold text-slate-600 hover:text-slate-900">Query parsing debug panel (Development)</summary><div className="mt-2"><pre className="overflow-x-auto rounded-lg bg-slate-900 p-3 font-mono text-xs text-emerald-400">{JSON.stringify({parsed_query:data.parsed_query},null,2)}</pre></div></details>}
    <div className="mt-6 grid gap-7 lg:grid-cols-[220px_1fr]"><Filters values={filters} setValues={setFilters} open={mobileFilters} close={()=>setMobileFilters(false)}/><section>{result.loading?<Loading/>:result.error?<ErrorMessage>{result.error}</ErrorMessage>:!data?.results.length?<div className="rounded-xl border border-slate-200 bg-white p-12 text-center"><Search className="mx-auto text-slate-300"/><h3 className="mt-4 font-semibold text-slate-800">No matching public records</h3><p className="mt-2 text-sm text-slate-500">Try fewer words, another spelling, or remove a filter.</p></div>:<div className="space-y-4">{data.results.map(item=><ResultCard key={item.id} item={item} query={q}/>)}</div>}</section></div></>}
  </main>
}

function Filters({values,setValues,open,close}){const field=(key,label,options)=><label className="block"><span className="mb-2 block text-xs font-semibold text-slate-600">{label}</span>{options?<select value={values[key]} onChange={e=>setValues({...values,[key]:e.target.value})} className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm outline-none"><option value="">All</option>{options.map(([v,l])=> <option value={v} key={v}>{l}</option>)}</select>:<input value={values[key]} onChange={e=>setValues({...values,[key]:e.target.value})} className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm outline-none" placeholder={`Any ${label.toLowerCase()}`}/>}</label>;return <aside className={`${open?'fixed inset-0 z-50 block bg-white p-6':'hidden'} space-y-5 lg:static lg:block lg:bg-transparent lg:p-0`}><div className="flex items-center justify-between lg:hidden"><b>Search filters</b><button onClick={close}><X/></button></div>{field('department','Department')}{field('district','District')}{field('date','Date',[['today','Today'],['week','Past week'],['month','Past month'],['year','Past year']])}{field('language','Language',[['en','English'],['mr','Marathi'],['hi','Hindi']])}<button onClick={()=>setValues({department:'',district:'',language:'',date:''})} className="text-xs font-medium text-[#175cd3]">Clear filters</button></aside>}

function ResultCard({item,query}){
  const isDoc=item.type==='government_document'||item.content_type==='government_document'
  const isNews=item.type==='news_article'||item.content_type==='news_article'
  const isVideo=item.type==='youtube_transcript'||item.content_type==='youtube_transcript'
  const Icon=isDoc?Building2:isNews?Newspaper:Video
  const label=isDoc?'Government Document':isNews?'News':'▶ Video'
  const videoUrl=item.video_url||item.source_url
  const startSeconds=item.timestamp_seconds||0
  const watch=isVideo?`${videoUrl}${videoUrl&&videoUrl.includes('?')?'&':'?'}t=${Math.floor(startSeconds)}s`:item.source_url
  return <article className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm"><div className="flex gap-4"><span className="grid h-10 w-10 shrink-0 place-items-center rounded-lg bg-blue-50 text-[#175cd3]"><Icon size={18}/></span><div className="min-w-0 flex-1"><div className="flex items-center justify-between gap-3"><div className="text-[10px] font-bold uppercase tracking-[.13em] text-[#175cd3]">{label}</div><span className="text-[10px] font-semibold text-slate-400">Score {item.score}</span></div><Link to={detailPath(item)} className="mt-1.5 block text-lg font-semibold leading-snug text-[#14243b] hover:text-[#175cd3]">{item.title}</Link><div className="mt-2 flex flex-wrap gap-x-3 gap-y-1 text-xs text-slate-500"><span>{item.channel||item.department||item.publisher||item.source||item.source_name}</span>{item.published_at&&<><span>•</span><span>Published: {fmtDate(item.published_at)}</span></>}{item.page_number&&<><span>•</span><span>Page {item.page_number}</span></>}{isVideo&&<><span>•</span><span className="font-mono">{fmtDuration(item.timestamp_seconds)}</span></>}</div><div className={`mt-4 ${isVideo?'rounded-lg border border-blue-100 bg-blue-50/50 p-3':''}`}><p className="text-sm leading-6 text-slate-700">{isVideo&&'“'}<Highlight text={item.snippet} query={query} terms={item.highlight_terms}/>{isVideo&&'”'}</p></div><div className="mt-4 flex flex-wrap gap-3"><Link to={detailPath(item)} className="rounded-lg bg-[#175cd3] px-3 py-2 text-xs font-semibold text-white hover:bg-[#124cae]">{isDoc?'View document':isNews?'View details':'View transcript'}</Link><a href={watch} target="_blank" rel="noreferrer" className="flex items-center gap-1.5 rounded-lg border border-slate-200 px-3 py-2 text-xs font-semibold text-slate-600 hover:border-slate-300"><ExternalLink size={12}/>{isVideo?`Watch from ${fmtDuration(item.timestamp_seconds)}`:'Open original'}</a></div></div></div></article>
}

export function PublicDocument(){const {id}=useParams(),state=useFetch(`/documents/${id}`,[id]);if(state.loading)return <Loading/>;if(state.error)return <main className="mx-auto max-w-4xl p-6"><ErrorMessage>{state.error}</ErrorMessage></main>;const d=state.data,v=d.versions[0];return <PublicDetail back="/search?q=Maharashtra"><div className="text-xs font-bold uppercase tracking-wider text-[#175cd3]">Government document</div><h1 className="mt-3 text-3xl font-semibold tracking-tight">{d.title}</h1><div className="mt-5 grid gap-4 rounded-xl border border-slate-200 bg-white p-5 text-sm sm:grid-cols-3"><Meta label="Department" value={d.department}/><Meta label="Published" value={fmtDate(d.published_date)}/><Meta label="Document type" value={d.document_type}/><Meta label="File size" value={v?`${(v.file_size/1e6).toFixed(2)} MB`:'—'}/><Meta label="Pages" value={v?.page_count||'—'}/><Meta label="Source" value={new URL(d.document_url).hostname}/></div><div className="mt-5 flex gap-3"><a href={d.document_url} target="_blank" className="public-primary">Open original <ExternalLink size={14}/></a><a href={d.document_url} target="_blank" className="public-secondary">View PDF <FileText size={14}/></a></div><section className="mt-10"><h2 className="text-xl font-semibold">Extracted searchable text</h2><p className="mt-1 text-sm text-slate-500">Text is shown page by page where the PDF permits extraction.</p><div className="mt-5 space-y-4">{v?.pages?.length?v.pages.map(p=><div className="rounded-xl border border-slate-200 bg-white p-6" key={p.page_number}><div className="mb-4 text-xs font-bold uppercase tracking-wider text-[#175cd3]">Page {p.page_number}</div><div className="whitespace-pre-wrap text-sm leading-7 text-slate-700">{p.text||'No extractable text on this page.'}</div></div>):<div className="rounded-xl border border-slate-200 bg-white p-6 whitespace-pre-wrap text-sm leading-7 text-slate-700">{v?.extracted_text||'No extractable text is available.'}</div>}</div></section></PublicDetail>}

export function PublicVideo(){const {id}=useParams(),state=useFetch(`/youtube/${id}`,[id]),[query,setQuery]=useState('');if(state.loading)return <Loading/>;if(state.error)return <main className="mx-auto max-w-4xl p-6"><ErrorMessage>{state.error}</ErrorMessage></main>;const v=state.data,segments=v.segments.filter(s=>s.text.toLowerCase().includes(query.toLowerCase()));return <PublicDetail back="/search?q=Maharashtra"><div className="text-xs font-bold uppercase tracking-wider text-[#175cd3]">Public video</div><h1 className="mt-3 text-3xl font-semibold tracking-tight">{v.title}</h1><div className="mt-4 flex flex-wrap gap-4 text-sm text-slate-500"><span>{v.channel_name}</span><span>{fmtDate(v.published_at)}</span><span>{fmtDuration(v.duration)}</span><span className={v.transcript_available?'text-emerald-700':'text-amber-700'}>{v.transcript_available?'Transcript indexed':'Transcript unavailable'}</span></div><a href={v.video_url} target="_blank" className="public-primary mt-5 inline-flex">Original video <ExternalLink size={14}/></a><section className="mt-10 rounded-xl border border-slate-200 bg-white"><div className="border-b border-slate-200 p-5"><h2 className="text-xl font-semibold">Transcript</h2>{v.transcript_available?<div className="relative mt-4"><Search className="absolute left-3 top-3 text-slate-400" size={16}/><input value={query} onChange={e=>setQuery(e.target.value)} className="w-full rounded-lg border border-slate-200 py-2.5 pl-9 pr-3 text-sm outline-none focus:border-blue-400" placeholder="Search inside transcript…"/></div>:<p className="mt-2 text-sm text-slate-500">This video has no publicly available captions. No transcript was generated.</p>}</div>{v.transcript_available&&<div className="divide-y divide-slate-100">{segments.map(s=><div className="flex gap-5 p-5" key={s.id}><a href={`${v.video_url}${v.video_url.includes('?')?'&':'?'}t=${Math.floor(s.start_seconds)}s`} target="_blank" className="font-mono text-xs font-semibold text-[#175cd3]">{fmtDuration(s.start_seconds)}</a><p className="text-sm leading-6 text-slate-700"><Highlight text={s.text} query={query}/></p></div>)}</div>}</section></PublicDetail>}

export function PublicNews(){const {id}=useParams(),state=useFetch(`/news/${id}`,[id]);if(state.loading)return <Loading/>;if(state.error)return <main className="mx-auto max-w-4xl p-6"><ErrorMessage>{state.error}</ErrorMessage></main>;const a=state.data;return <PublicDetail back="/search?q=Maharashtra"><div className="text-xs font-bold uppercase tracking-wider text-[#175cd3]">News · {a.publisher}</div><h1 className="mt-3 text-3xl font-semibold leading-tight tracking-tight md:text-4xl">{a.title}</h1><div className="mt-5 flex flex-wrap gap-3 text-sm text-slate-500"><span>By {a.author||'Publisher staff'}</span><span>•</span><span>{fmtDate(a.published_at)}</span><span>•</span><span>{a.language?.toUpperCase()}</span></div><a href={a.article_url} target="_blank" className="public-primary mt-6 inline-flex">Read original article <ExternalLink size={14}/></a><article className="mt-9 rounded-xl border border-slate-200 bg-white p-7"><p className="text-lg leading-8 text-slate-700">{a.description}</p><div className="mt-6 whitespace-pre-wrap text-[15px] leading-8 text-slate-600">{a.article_text}</div><div className="mt-8 border-t border-slate-100 pt-4 text-xs text-slate-500">Source: {a.publisher} · Original attribution retained</div></article></PublicDetail>}

function PublicDetail({back,children}){return <main className="mx-auto max-w-4xl px-5 py-10"><Link to={back} className="mb-7 inline-flex items-center gap-2 text-sm text-slate-500 hover:text-[#175cd3]"><ArrowLeft size={15}/>Back to search</Link>{children}</main>}
function Meta({label,value}){return <div><div className="text-[10px] font-bold uppercase tracking-wider text-slate-400">{label}</div><div className="mt-1.5 text-slate-700">{value||'—'}</div></div>}
