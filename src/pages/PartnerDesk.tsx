
import { useState, type CSSProperties } from 'react'
import { Helmet } from 'react-helmet-async'
import { parseRows, assess, approvedCSV, type Assessment } from '../lib/partner-pilot'
import { makeQualificationPrompt, makePersonalizationPrompt, parseQualification, parsePersonalization, type Qualification, type PersonalizedDraft, type AIStage } from '../lib/partner-ai-workflow'

const panel:CSSProperties={background:'#17291e',border:'1px solid #45654d',borderRadius:12,padding:20,marginBottom:16}
const btn:CSSProperties={background:'#335a3d',border:'1px solid #719a76',borderRadius:8,color:'white',padding:'9px 15px',cursor:'pointer',marginRight:8,marginBottom:8}
const field:CSSProperties={width:'100%',boxSizing:'border-box',padding:11,background:'#0a1b10',color:'white',border:'1px solid #608369',borderRadius:8,margin:'7px 0'}
const muted:CSSProperties={fontSize:14,color:'#cadece'}

export default function PartnerPilot(){
  const [sourceText,setSourceText]=useState('')
  const [items,setItems]=useState<Assessment[]>([])
  const [errors,setErrors]=useState<string[]>([])
  const [selected,setSelected]=useState('')
  const [sourcesVerified,setSourcesVerified]=useState<Set<string>>(new Set())
  const [qualInputs,setQualInputs]=useState<Record<string,string>>({})
  const [quals,setQuals]=useState<Record<string,Qualification>>({})
  const [qualApproved,setQualApproved]=useState<Set<string>>(new Set())
  const [draftInputs,setDraftInputs]=useState<Record<string,string>>({})
  const [drafts,setDrafts]=useState<Record<string,PersonalizedDraft>>({})
  const [draftApproved,setDraftApproved]=useState<Set<string>>(new Set())
  const [operator,setOperator]=useState('')
  const [message,setMessage]=useState('')
  const item=items.find(x=>x.id===selected)
  const qualification=item?quals[item.id]:undefined
  const draft=item?drafts[item.id]:undefined
  const qualified=!!(item&&sourcesVerified.has(item.id)&&qualApproved.has(item.id)&&qualification?.disposition==='fit')
  const eligible=items.filter(x=>{if(!sourcesVerified.has(x.id)||!qualApproved.has(x.id)||quals[x.id]?.disposition!=='fit'||!drafts[x.id]||!draftApproved.has(x.id)||!x.reviewable)return false;try{parsePersonalization(JSON.stringify(drafts[x.id]),x.partner);return true}catch{return false}})
  const reviewable=items.filter(x=>x.reviewable).length

  function reset(){setItems([]);setErrors([]);setSelected('');setSourcesVerified(new Set());setQualInputs({});setQuals({});setQualApproved(new Set());setDraftInputs({});setDrafts({});setDraftApproved(new Set());setMessage('')}
  function load(){
    const parsed=parseRows(sourceText)
    const assessments=parsed.partners.map(assess).sort((a,b)=>b.score-a.score)
    reset()
    setItems(assessments)
    setErrors(parsed.errors)
    setSelected(assessments[0]?.id||'')
  }
  function markSource(ok:boolean){
    if(!item)return
    const next=new Set(sourcesVerified)
    if(ok)next.add(item.id);else next.delete(item.id)
    setSourcesVerified(next)
    if(!ok){
      const aq=new Set(qualApproved);aq.delete(item.id);setQualApproved(aq)
      const ad=new Set(draftApproved);ad.delete(item.id);setDraftApproved(ad)
    }
  }
  async function copyPrompt(stage:AIStage){
    if(!item)return
    const prompt=stage==='qualify'?makeQualificationPrompt(item.partner):makePersonalizationPrompt(item.partner,qualification!)
    try{await navigator.clipboard.writeText(prompt);setMessage('AI prompt copied. Paste into your chosen AI assistant, then paste its JSON response here.')}
    catch{setMessage('Clipboard access blocked; copy the prompt from the text area.')}
  }
  async function importAIJSON(stage:AIStage,file:File){
    if(!item)return
    if(file.size>7000){setMessage('AI JSON file exceeds the 7 KB safety limit');return}
    const raw=await file.text()
    if(stage==='qualify'){
      setQualInputs(prev=>({...prev,[item.id]:raw}))
      setQuals(prev=>{const n={...prev};delete n[item.id];return n})
      const aq=new Set(qualApproved);aq.delete(item.id);setQualApproved(aq)
      const ad=new Set(draftApproved);ad.delete(item.id);setDraftApproved(ad)
      setDrafts(prev=>{const n={...prev};delete n[item.id];return n})
    }else{
      setDraftInputs(prev=>({...prev,[item.id]:raw}))
      setDrafts(prev=>{const n={...prev};delete n[item.id];return n})
      const ad=new Set(draftApproved);ad.delete(item.id);setDraftApproved(ad)
    }
    setMessage('AI '+(stage==='qualify'?'qualification':'draft')+' JSON imported. Click Validate to apply; nothing has been approved automatically.')
  }
  function acceptManual(stage:AIStage){
    if(!item)return
    try{
      if(stage==='qualify'){
        const q=parseQualification(qualInputs[item.id]||'',item.partner)
        setQuals(previous=>({...previous,[item.id]:q}))
        const aq=new Set(qualApproved);aq.delete(item.id);setQualApproved(aq)
        const ad=new Set(draftApproved);ad.delete(item.id);setDraftApproved(ad)
        setDrafts(previous=>{const next={...previous};delete next[item.id];return next})
        setMessage('Stage 1 validated. Verify the source and review the qualification before approving Stage 2.')
      }else{
        if(!qualified)throw new Error('Approve a fit qualification first')
        const d=parsePersonalization(draftInputs[item.id]||'',item.partner)
        setDrafts(previous=>({...previous,[item.id]:d}))
        const ad=new Set(draftApproved);ad.delete(item.id);setDraftApproved(ad)
        setMessage('Stage 2 validated. Review the proposed email and approve for export only.')
      }
    }catch(e){setMessage(e instanceof Error?e.message:'Invalid AI response')}
  }
  function download(name:string,contents:string,mime:string){
    const blob=new Blob([contents],{type:mime})
    const url=URL.createObjectURL(blob)
    const a=document.createElement('a');a.href=url;a.download=name
    document.body.appendChild(a);a.click();a.remove();URL.revokeObjectURL(url)
  }
  function exportPack(){
    if(!eligible.length||operator.trim().length<3)return
    const mapped=eligible.map(x=>({...x,subject:drafts[x.id].subject,body:drafts[x.id].body}))
    download('klearpath-ai-reviewed-outreach-DRAFT-ONLY.csv',approvedCSV(mapped,new Set(eligible.map(x=>x.id))),'text/csv;charset=utf-8')
    const receipt={kind:'OPERATOR_SELF_ATTESTED_DRAFT_EXPORT_NOT_SENT',organization:'Klear Path',operator:operator.trim(),timestamp:new Date().toISOString(),count:eligible.length,items:eligible.map(x=>({organization:x.partner.organization,source:x.partner.source,category:x.partner.category,stage1:quals[x.id],stage2:drafts[x.id],status:'DRAFT_EXPORTED_NOT_SENT'})),disclaimer:'This receipt does not prove message delivery, team/client acceptance, or commercial results. Obtain independent organizational confirmation.'}
    download('klearpath-ai-operator-draft-receipt.json',JSON.stringify(receipt,null,2),'application/json')
    setMessage('Drafts and operator self-attestation downloaded. No messages sent. Preserve both files in Klear Path-controlled storage.')
  }
  const canAdvance=!!(item&&item.reviewable&&sourcesVerified.has(item.id))
  return <main style={{background:'#0b1610',color:'#f1f6ef',minHeight:'100vh',padding:22,fontFamily:'system-ui,sans-serif'}}>
    <div style={{maxWidth:1000,margin:'auto'}}>
      <Helmet><title>Partner Development Desk | Klear Path</title><meta name="robots" content="noindex,nofollow" /></Helmet>
      <a href="/" style={{color:'#b3e1bd',fontSize:14}}>← Klear Path Home</a>
      <p style={muted}>KLEAR PATH · PARTNER DEVELOPMENT · NO AUTOMATIC OUTREACH</p>
      <h1>AI Partner Development Workflow</h1>
      <p style={muted}>A practical Klear Path partnership workflow: verified public research → AI qualification → review and approval → personalized outreach using that qualification → final approval and export. Use your approved AI assistant for the two steps. Your research stays in this browser session; no automatic sending, uploads, or charges. Do not enter private participant, beneficiary, donor, or health information.</p>

      <section style={panel}>
        <h2>1. Import actual partner research</h2>
        <p style={muted}>Import your verified public-business research (TSV/TXT) or enter genuine records. Organization | Category | Website | Email | Research evidence | Source URL | Region. Source URLs are supplied by the operator and must be independently checked.</p>
        <textarea aria-label="Public partnership research" value={sourceText} onChange={e=>{setSourceText(e.target.value);reset()}} rows={5} style={field}/>
        <label style={muted}>Import a research batch (TSV/TXT, maximum 150 KB)</label>
        <input aria-label="Import public research batch" type="file" accept=".tsv,.txt" style={{display:'block',margin:'10px 0'}} onChange={async e=>{
          const control=e.currentTarget;const file=control.files?.[0];if(!file)return
          if(file.size>150000){setMessage('Import limit is 150 KB');control.value='';return}
          const content=await file.text();reset();setSourceText(content);control.value=''
        }}/>
        <button style={btn} disabled={!sourceText.trim()} onClick={load}>Qualify supplied records</button>

        {errors.length>0&&<div role="alert" style={{color:'#ffcba8'}}>{errors.map((e,i)=><p key={i}>{e}</p>)}</div>}
      </section>

      {items.length>0&&<section style={panel}>
        <h2>2. Select research and verify its source</h2>
        <p style={muted}>{items.length} records parsed; {reviewable} have contact/source/context fields; {eligible.length} approved AI drafts ready to export. Completeness score is NOT buyer-fit or verified evidence.</p>
        <select aria-label="Selected organization" style={field} value={selected} onChange={e=>{setSelected(e.target.value);setMessage('')}}>
          {items.map(x=><option value={x.id} key={x.id}>{x.partner.organization} · {x.partner.category} · {x.reviewable?'reviewable':'hold'}</option>)}
        </select>
        {item&&<>
          <p style={muted}>Reported context (unverified): {item.partner.evidence}</p>
          <p><a style={{color:'#b3e1bd'}} href={item.partner.source||'#'} target="_blank" rel="noreferrer">Open source provided by operator</a></p>
          <label><input type="checkbox" checked={sourcesVerified.has(item.id)} onChange={e=>markSource(e.target.checked)} disabled={!item.reviewable}/> I personally checked this source and the public business contact for accuracy and relevance.</label>
        </>}
      </section>}

      {item&&<section style={panel}>
        <h2>3. AI stage A — partnership qualification</h2>
        <p style={muted}>Use an approved AI assistant in a separate tab. Copy the qualification prompt and paste the resulting JSON below. Your judgment and source verification remain required.</p>
        <button style={btn} disabled={!canAdvance} onClick={()=>copyPrompt('qualify')}>Copy qualification prompt</button>
        <textarea aria-label="Qualification AI prompt" readOnly value={makeQualificationPrompt(item.partner)} rows={5} style={field}/>
        <label style={muted}>Or import AI qualification JSON from a local file:</label>
        <input aria-label="Import stage A AI JSON" type="file" accept=".json,application/json" style={{display:'block',margin:'8px 0'}} onChange={async e=>{const input=e.currentTarget;const f=input.files?.[0];if(f)await importAIJSON('qualify',f);input.value=''}}/>
        <label style={muted}>AI qualification JSON (from manual assistant)</label>
        <textarea aria-label="Paste AI qualification JSON" value={qualInputs[item.id]||''} onChange={e=>setQualInputs(p=>({...p,[item.id]:e.target.value}))} rows={5} style={field}/>
        <button style={btn} disabled={!canAdvance} onClick={()=>acceptManual('qualify')}>Validate pasted AI qualification</button>
        {qualification&&<div style={{padding:12,border:'1px solid #688b6d',borderRadius:8}}>
          <p><strong>Recommendation: {qualification.disposition}</strong></p>
          <p>{qualification.rationale}</p>
          <p>Evidence quote: {qualification.evidenceQuote||'None cited'}</p>
          <p>Proposed angle: {qualification.recommendedAngle}</p>
          <p>Needs verification: {qualification.verificationNeeded||'None declared'}</p>
          <label><input type="checkbox" checked={qualApproved.has(item.id)} disabled={!canAdvance||qualification.disposition!=='fit'} onChange={e=>{const n=new Set(qualApproved);if(e.target.checked)n.add(item.id);else n.delete(item.id);setQualApproved(n);const d=new Set(draftApproved);d.delete(item.id);setDraftApproved(d)}}/> Human-approve this fit qualification for AI drafting</label>
        </div>}
      </section>}

      {item&&<section style={panel}>
        <h2>4. AI stage B — personalize from the approved stage A result</h2>
        <p style={muted}>Stage B uses the approved Stage A qualification and the original research evidence. Review the personalized response before exporting it.</p>
        <button style={btn} disabled={!qualified} onClick={()=>copyPrompt('personalize')}>Copy personalized outreach prompt</button>
        {qualified&&<textarea aria-label="Personalization AI prompt" readOnly value={makePersonalizationPrompt(item.partner,qualification!)} rows={5} style={field}/>}
        <label style={muted}>Or import AI personalized outreach JSON from a local file:</label>
        <input aria-label="Import stage B AI JSON" type="file" accept=".json,application/json" disabled={!qualified} style={{display:'block',margin:'8px 0'}} onChange={async e=>{const input=e.currentTarget;const f=input.files?.[0];if(f)await importAIJSON('personalize',f);input.value=''}}/>
        <label style={muted}>AI personalization JSON (manual assistant)</label>
        <textarea aria-label="Paste AI personalization JSON" value={draftInputs[item.id]||''} onChange={e=>setDraftInputs(p=>({...p,[item.id]:e.target.value}))} rows={5} style={field} disabled={!qualified}/>
        <button style={btn} disabled={!qualified} onClick={()=>acceptManual('personalize')}>Validate pasted AI draft</button>
        {draft&&<>
          <p style={muted}>Draft subject</p><input aria-label="Edit reviewed subject" style={field} value={draft.subject} onChange={e=>{setDrafts(p=>({...p,[item.id]:{...draft,subject:e.target.value}}));setDraftApproved(p=>{const n=new Set(p);n.delete(item.id);return n})}}/>
          <p style={muted}>Draft body — never sent from this application</p><textarea aria-label="Edit reviewed message" rows={9} style={field} value={draft.body} onChange={e=>{setDrafts(p=>({...p,[item.id]:{...draft,body:e.target.value}}));setDraftApproved(p=>{const n=new Set(p);n.delete(item.id);return n})}}/>
          <p style={muted}>Verbatim evidence cited: {draft.evidenceQuote||'None cited'}</p>
          <label><input type="checkbox" checked={draftApproved.has(item.id)} disabled={!qualified||draft.subject.length>110||draft.body.length>1600||!draft.subject.trim()||!draft.body.trim()} onChange={e=>{const n=new Set(draftApproved);if(e.target.checked)n.add(item.id);else n.delete(item.id);setDraftApproved(n)}}/> Human-approve this final draft for export ONLY (no permission to send)</label>
        </>}
      </section>}

      {items.length>0&&<section style={panel}>
        <h2>5. Export documented drafts, not alleged results</h2>
        <label htmlFor="pilot-operator">Operator name (self-attested; no external authentication of identity)</label>
        <input id="pilot-operator" style={field} value={operator} onChange={e=>setOperator(e.target.value)} placeholder="Actual Klear Path operator"/>
        <button style={btn} disabled={!eligible.length||operator.trim().length<3} onClick={exportPack}>Export {eligible.length} AI-reviewed draft{eligible.length===1?'':'s'} + audit receipt</button>
        <p style={muted}>Receipts document a review and export only. They do not establish independent organizational use, message delivery, team approval, or financial results. No messages or CRM records are sent.</p>
      </section>}
      {message&&<p role="status" style={{padding:14,background:'#25412b',borderRadius:10}}>{message}</p>}
    </div>
  </main>
}
