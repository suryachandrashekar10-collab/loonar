import { useState } from 'react'
import { Search, BookOpen, FileText, Tag, Clock, ArrowRight } from 'lucide-react'

const DOCS = [
  { id: 1, title: 'Shell LNG Terminal — Valve Package Proposal', type: 'Past Proposal', tags: ['API 6D', 'NACE MR0175', 'Duplex SS'], date: '2024-11-12', pages: 142, relevance: 97 },
  { id: 2, title: 'Petrobras Refinery — Pump Package Deviation List', type: 'Deviation List', tags: ['API 610', 'ASME B16.5', 'Centrifugal'], date: '2024-08-03', pages: 28, relevance: 91 },
  { id: 3, title: 'ADNOC Gas Processing — Valve Clarification Register', type: 'Clarification', tags: ['NACE MR0175', 'Carbon Steel'], date: '2023-12-19', pages: 34, relevance: 88 },
  { id: 4, title: 'Exxon Beaumont — Actuation Package Proposal', type: 'Past Proposal', tags: ['Pneumatic', 'API 6A', 'Low-temp'], date: '2024-03-07', pages: 87, relevance: 82 },
  { id: 5, title: 'Product Manual — Triple-Offset Butterfly Valves Rev 7', type: 'Product Manual', tags: ['API 609', 'High-temp', 'PTFE'], date: '2025-01-15', pages: 203, relevance: 76 },
]

const typeColor: Record<string, string> = {
  'Past Proposal': 'text-brand-400 bg-brand-500/10',
  'Deviation List': 'text-amber-400 bg-amber-500/10',
  'Clarification':  'text-purple-400 bg-purple-500/10',
  'Product Manual': 'text-emerald-400 bg-emerald-500/10',
}

export default function ContentLibrary() {
  const [query, setQuery] = useState('')
  const [searched, setSearched] = useState(false)

  const results = searched
    ? DOCS.sort((a, b) => b.relevance - a.relevance)
    : []

  return (
    <div className="p-8">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-white">Content Library</h1>
        <p className="text-slate-400 text-sm mt-1">Semantic search across past proposals, deviation lists, manuals, and supplier quotations.</p>
      </div>

      {/* Search */}
      <div className="relative mb-8">
        <Search size={16} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" />
        <input
          value={query}
          onChange={e => setQuery(e.target.value)}
          onKeyDown={e => { if (e.key === 'Enter' && query.trim()) setSearched(true) }}
          placeholder='Try: "Find similar offers where we addressed NACE MR0175" or "Low-temperature carbon steel deviations"'
          className="w-full bg-panel border border-border rounded-xl pl-10 pr-4 py-3.5 text-sm text-white placeholder-slate-600 focus:outline-none focus:border-brand-500 transition-colors"
        />
        <button
          onClick={() => { if (query.trim()) setSearched(true) }}
          className="absolute right-3 top-1/2 -translate-y-1/2 px-3 py-1.5 bg-brand-500 hover:bg-brand-600 text-white text-xs font-medium rounded-lg transition-colors"
        >
          Search
        </button>
      </div>

      {!searched && (
        <div className="grid grid-cols-3 gap-4">
          {[
            { label: 'Total Documents', value: '234', icon: BookOpen, color: 'text-brand-400' },
            { label: 'Past Proposals',  value: '87',  icon: FileText, color: 'text-amber-400' },
            { label: 'Indexed Tags',    value: '1.2k', icon: Tag,     color: 'text-emerald-400' },
          ].map(({ label, value, icon: Icon, color }) => (
            <div key={label} className="bg-panel border border-border rounded-xl p-5">
              <Icon size={16} className={`${color} mb-3`} />
              <div className="text-2xl font-semibold text-white">{value}</div>
              <div className="text-xs text-slate-500 mt-1">{label}</div>
            </div>
          ))}
          <div className="col-span-3 bg-panel border border-border rounded-xl p-6">
            <p className="text-sm text-slate-400 mb-3">Suggested searches</p>
            <div className="flex flex-wrap gap-2">
              {[
                'NACE MR0175 deviations accepted by Shell',
                'Low-temperature carbon steel ASTM A350',
                'Class 900 RTJ flange alternatives',
                'API 610 centrifugal pump past proposals',
                'Bureau Veritas TPI alternatives',
              ].map(s => (
                <button
                  key={s}
                  onClick={() => { setQuery(s); setSearched(true) }}
                  className="text-xs px-3 py-1.5 bg-white/5 border border-border rounded-full text-slate-400 hover:text-white hover:border-brand-500/40 transition-colors"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {searched && (
        <div>
          <div className="flex items-center justify-between mb-4">
            <p className="text-sm text-slate-400">
              <span className="text-white font-medium">{results.length} results</span> for "{query}"
            </p>
            <button onClick={() => { setSearched(false); setQuery('') }} className="text-xs text-slate-500 hover:text-slate-300">Clear</button>
          </div>
          <div className="space-y-3">
            {results.map(doc => (
              <div key={doc.id} className="bg-panel border border-border rounded-xl p-5 hover:border-brand-500/40 transition-colors cursor-pointer group">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <span className={`text-xs px-2 py-0.5 rounded-md font-medium ${typeColor[doc.type]}`}>{doc.type}</span>
                      <div className="flex items-center gap-1 text-xs text-slate-600">
                        <Clock size={10} />
                        {doc.date}
                      </div>
                      <span className="text-xs text-slate-600">· {doc.pages} pages</span>
                    </div>
                    <h3 className="text-sm font-medium text-white group-hover:text-brand-300 transition-colors">{doc.title}</h3>
                    <div className="flex flex-wrap gap-1.5 mt-2">
                      {doc.tags.map(t => (
                        <span key={t} className="text-xs px-1.5 py-0.5 bg-white/5 border border-border rounded text-slate-500">{t}</span>
                      ))}
                    </div>
                  </div>
                  <div className="flex-shrink-0 text-right">
                    <div className="text-lg font-semibold text-emerald-400">{doc.relevance}%</div>
                    <div className="text-xs text-slate-600">relevance</div>
                    <ArrowRight size={14} className="text-brand-400 ml-auto mt-2 opacity-0 group-hover:opacity-100 transition-opacity" />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
