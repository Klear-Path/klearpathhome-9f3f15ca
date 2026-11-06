/** Klear Path partner development pilot. Pure logic; no sends, server writes, or secret access. */
export const PARTNER_TYPES = ['sponsor','employer','service_partner'] as const;
export type PartnerType = typeof PARTNER_TYPES[number];
export type Partner = {organization:string;category:PartnerType;website:string;email:string;evidence:string;source:string;region:string};
export type Assessment = {id:string;partner:Partner;score:number;reviewable:boolean;reason:string[];subject:string;body:string};
const EMAIL=/^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const REGION=/(montgomery|bucks|philadelphia|delaware county|chester county|greater philadelphia|pennsylvania|\bpa\b)/i;
export function validWebUrl(value:string):boolean {
  if (!value || /[\r\n\t]/.test(value)) return false;
  try { const url=new URL(value);return ['http:','https:'].includes(url.protocol)&&!!url.hostname&&!url.username&&!url.password; }catch{return false;}
}
export function normalizeType(value:string):PartnerType|null {
  const v=value.trim().toLowerCase().replace(/[ -]+/g,'_');
  if (['sponsor','donor','corporate_sponsor'].includes(v)) return 'sponsor';
  if (['employer','workforce'].includes(v)) return 'employer';
  if (['service_partner','referral','referral_partner','service'].includes(v)) return 'service_partner';
  return null;
}
export function parseRows(text:string):{partners:Partner[];errors:string[]} {
  const partners:Partner[]=[],errors:string[]=[],seen=new Set<string>();
  text.split(/\r?\n/).forEach((raw,index)=>{
    if (!raw.trim()) return;
    const parts=raw.split(raw.includes('\t')?'\t':'|').map(s=>s.trim());
    if (parts.length!==7){errors.push('Line '+(index+1)+': expected seven fields.');return;}
    const [organization,type,website,email,evidence,source,region]=parts;
    if(organization.toLowerCase()==='organization'&&index===0)return;
    const category=normalizeType(type);
    if(!organization||organization.length>140||!category){errors.push('Line '+(index+1)+': invalid organization or category.');return;}
    if(website&&!validWebUrl(website)){errors.push('Line '+(index+1)+': invalid website.');return;}
    if(source&&!validWebUrl(source)){errors.push('Line '+(index+1)+': invalid source URL.');return;}
    if(email&&!EMAIL.test(email)){errors.push('Line '+(index+1)+': invalid email format.');return;}
    const key=category+'|'+organization.toLowerCase()+'|'+email.toLowerCase();
    if(seen.has(key)){errors.push('Line '+(index+1)+': duplicate partner/contact/category.');return;}
    seen.add(key);
    partners.push({organization,category,website,email,evidence,source,region});
  });
  return {partners,errors};
}
export function draft(partner:Partner):{subject:string;body:string} {
  const greeting='Hello '+partner.organization+' team,\n\n';
  const sign='\n\nKlear Path | klearpathhome.org';
  if(partner.category==='sponsor')return {
    subject:'Exploring a community partnership with Klear Path',
    body:greeting+'Klear Path is developing a stability-first housing stabilization and workforce reintegration pilot in the Greater Philadelphia area. We are identifying potential corporate and community partners.\n\nWould your team be open to a short discussion about your community-investment or sponsorship process?\n\nOur initiative is early-stage; planned pilot capacity and future housing facilities are not represented as operational.'+sign
  };
  if(partner.category==='employer')return {
    subject:'Exploring workforce partnerships in Greater Philadelphia',
    body:greeting+'Klear Path is developing a housing stabilization and workforce reintegration pilot in the Greater Philadelphia area. We are exploring future employer partnerships and work-readiness pathways.\n\nWould you be open to a brief conversation about typical hiring requirements and potential cooperation?\n\nThis inquiry is not a claim of existing placement capacity or guaranteed candidates.'+sign
  };
  return {
    subject:'Exploring a local stabilization and referral partnership',
    body:greeting+'Klear Path is developing a stability-first housing and workforce reintegration pilot for the Greater Philadelphia area. We are mapping complementary services and potential referral partners.\n\nWould you be open to a brief conversation about your programs, referral criteria, and possible cooperation?\n\nThe program is in development; no service or referral commitment is implied.'+sign
  };
}
/** Completeness heuristic only; no claim that research or contact information has been verified. */
export function assess(partner:Partner,index:number):Assessment {
  const reason:string[]=[];let score=partner.category==='service_partner'?15:20;
  reason.push('Relevant partnership category supplied');
  if(partner.email&&EMAIL.test(partner.email)){score+=20;reason.push('Contact address supplied; ownership/deliverability not verified');}
  if(partner.website&&validWebUrl(partner.website)){score+=10;reason.push('Website supplied; not independently visited');}
  if(partner.source&&validWebUrl(partner.source)){score+=20;reason.push('Source URL supplied; content not independently verified');}
  if(partner.evidence.length>=35){score+=20;reason.push('Context supplied; independent fact-check needed');}
  if(REGION.test(partner.region)){score+=10;reason.push('Region appears to match service area');}
  const reviewable=!!partner.email&&!!partner.source&&partner.evidence.length>=35;
  if(!reviewable)reason.push('HOLD: contact + source URL + substantial context required');
  const d=draft(partner);
  return {id:index+':'+partner.category+':'+partner.organization.toLowerCase()+':'+partner.email.toLowerCase(),partner,score,reviewable,reason,subject:d.subject,body:d.body};
}
function cell(value:string):string {
  const escaped=/^[\s\u0000-\u001f]*[=+\-@]/.test(value)?"'"+value:value;
  return '"'+escaped.replace(/"/g,'""')+'"';
}
/** Even approved export is a DRAFT ONLY: no transmission and no CRM writes. */
export function approvedCSV(items:Assessment[],approved:ReadonlySet<string>):string {
  const rows:string[][]=[['Organization','Category','Website','Email','Evidence','Source','Region','Score','Status','Subject','Draft']];
  for(const item of items){
    if(!approved.has(item.id)||!item.reviewable)continue;
    const p=item.partner;
    rows.push([p.organization,p.category,p.website,p.email,p.evidence,p.source,p.region,String(item.score),'HUMAN_APPROVED_DRAFT_ONLY_NOT_SENT',item.subject,item.body]);
  }
  return rows.map(r=>r.map(cell).join(',')).join('\r\n')+'\r\n';
}
