import { Link } from "react-router-dom";
import { Layout } from "@/components/layout/Layout";
import { Button } from "@/components/ui/button";
import { Shield, Home, Briefcase, ArrowRight, FileText, MessageSquare, Users, Clock, Target, TrendingUp, CheckCircle2, Building2, Cpu, ClipboardList, BarChart3, FileSearch } from "lucide-react";

const Index = () => {
  return (
    <Layout>
      {/* Hero Section */}
      <section className="relative bg-primary text-primary-foreground">
        <div className="container-wide section-padding py-20 lg:py-28">
          <div className="max-w-3xl animate-fade-in-up">
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-serif font-bold leading-tight mb-4">
              Klear Path
            </h1>
            <p className="text-xl sm:text-2xl font-serif text-primary-foreground/90 mb-6">
              Structured Housing & Workforce Infrastructure
            </p>
            <p className="text-lg text-primary-foreground/80 mb-10 max-w-2xl leading-relaxed">
              A federally recognized 501(c)(3) public charity focused on permanent village-based reintegration campuses in Bucks & Montgomery Counties, PA.
            </p>
            <div className="flex flex-col sm:flex-row gap-4">
              <a href="/klearpath_501c3.pdf" target="_blank" rel="noopener noreferrer">
                <Button variant="hero" size="xl">
                  <FileText className="w-5 h-5" />
                  Download Mission Brief
                </Button>
              </a>
              <Link to="/contact">
                <Button variant="hero-outline" size="xl">
                  <MessageSquare className="w-5 h-5" />
                  Request Strategic Conversation
                </Button>
              </Link>
            </div>
          </div>
        </div>

        {/* Credibility Bar */}
        <div className="border-t border-primary-foreground/15">
          <div className="container-wide section-padding py-6">
            <div className="grid sm:grid-cols-3 gap-4 text-sm text-primary-foreground/80">
              <p>Homelessness in Bucks & Montgomery Counties has nearly doubled in five years.</p>
              <p>The current system is reactive.</p>
              <p className="font-semibold text-primary-foreground">Klear Path builds structured alternatives.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Problem Section */}
      <section className="py-16 lg:py-24 bg-background">
        <div className="container-wide section-padding">
          <div className="max-w-4xl">
            <h2 className="text-3xl lg:text-4xl font-serif font-bold text-foreground mb-6">
              The Cost of System Fragmentation
            </h2>
            <p className="text-lg text-muted-foreground leading-relaxed mb-8">
              Bucks & Montgomery Counties' existing homelessness response relies on disconnected emergency 
              interventions. Without structured stabilization pathways, individuals cycle through 
              shelters, emergency rooms, and the criminal justice system—at significant public cost 
              and with minimal long-term outcomes.
            </p>
            <div className="grid sm:grid-cols-2 gap-6">
              <div className="bg-card border border-border rounded-xl p-6">
                <p className="text-3xl font-serif font-bold text-primary mb-2">400+</p>
                <p className="text-muted-foreground text-sm">Individuals identified in the latest Point-in-Time count</p>
              </div>
              <div className="bg-card border border-border rounded-xl p-6">
                <p className="text-3xl font-serif font-bold text-primary mb-2">~2×</p>
                <p className="text-muted-foreground text-sm">Increase in unsheltered homelessness over five years</p>
              </div>
              <div className="bg-card border border-border rounded-xl p-6">
                <p className="text-3xl font-serif font-bold text-primary mb-2">$50K–$80K</p>
                <p className="text-muted-foreground text-sm">Estimated annual public cost per chronically homeless individual</p>
              </div>
              <div className="bg-card border border-border rounded-xl p-6">
                <p className="text-3xl font-serif font-bold text-primary mb-2">High</p>
                <p className="text-muted-foreground text-sm">Recidivism rate driven by fragmented service delivery</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Three-Phase Model */}
      <section className="py-16 lg:py-24 bg-secondary">
        <div className="container-wide section-padding">
          <div className="mb-12">
            <h2 className="text-3xl lg:text-4xl font-serif font-bold text-foreground mb-4">
              Phased Stabilization Model
            </h2>
            <p className="text-lg text-muted-foreground max-w-3xl">
              A structured, outcome-oriented framework that moves individuals from crisis 
              to independence through defined phases with clear milestones.
            </p>
          </div>

          <div className="grid lg:grid-cols-3 gap-6">
            {/* Phase 1 */}
            <div className="bg-card rounded-xl border border-border p-8 relative">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center">
                  <Shield className="w-6 h-6 text-primary" />
                </div>
                <div>
                  <p className="text-xs font-semibold uppercase tracking-wider text-primary">Phase 1</p>
                  <h3 className="text-lg font-serif font-semibold text-foreground">Stabilization</h3>
                </div>
              </div>
              <div className="flex items-center gap-2 text-sm text-muted-foreground mb-4">
                <Clock className="w-4 h-4" />
                <span>0–30 Days</span>
              </div>
              <p className="text-muted-foreground text-sm leading-relaxed mb-4">
                Immediate safety, hygiene access, intake assessment, structured onboarding.
              </p>
              <div className="border-t border-border pt-4 space-y-2">
                <div className="flex items-start gap-2 text-sm">
                  <Target className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                  <span className="text-muted-foreground"><span className="font-medium text-foreground">Outcome:</span> Safe baseline established</span>
                </div>
                <div className="flex items-start gap-2 text-sm">
                  <CheckCircle2 className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                  <span className="text-muted-foreground"><span className="font-medium text-foreground">Purpose:</span> Remove immediate crisis barriers</span>
                </div>
              </div>
            </div>

            {/* Phase 2 */}
            <div className="bg-card rounded-xl border border-border p-8 relative">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center">
                  <Home className="w-6 h-6 text-primary" />
                </div>
                <div>
                  <p className="text-xs font-semibold uppercase tracking-wider text-primary">Phase 2</p>
                  <h3 className="text-lg font-serif font-semibold text-foreground">Structured Pod Residency</h3>
                </div>
              </div>
              <div className="flex items-center gap-2 text-sm text-muted-foreground mb-4">
                <Clock className="w-4 h-4" />
                <span>30–90 Days</span>
              </div>
              <p className="text-muted-foreground text-sm leading-relaxed mb-4">
                Private micro-units, defined expectations, case management, stability routines.
              </p>
              <div className="border-t border-border pt-4 space-y-2">
                <div className="flex items-start gap-2 text-sm">
                  <Target className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                  <span className="text-muted-foreground"><span className="font-medium text-foreground">Outcome:</span> Structured daily living maintained</span>
                </div>
                <div className="flex items-start gap-2 text-sm">
                  <CheckCircle2 className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                  <span className="text-muted-foreground"><span className="font-medium text-foreground">Purpose:</span> Build capacity for self-management</span>
                </div>
              </div>
            </div>

            {/* Phase 3 */}
            <div className="bg-card rounded-xl border border-border p-8 relative">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center">
                  <Briefcase className="w-6 h-6 text-primary" />
                </div>
                <div>
                  <p className="text-xs font-semibold uppercase tracking-wider text-primary">Phase 3</p>
                  <h3 className="text-lg font-serif font-semibold text-foreground">Workforce Integration</h3>
                </div>
              </div>
              <div className="flex items-center gap-2 text-sm text-muted-foreground mb-4">
                <Clock className="w-4 h-4" />
                <span>90–365 Days</span>
              </div>
              <p className="text-muted-foreground text-sm leading-relaxed mb-4">
                Skill development, income pathway, transition planning.
              </p>
              <div className="border-t border-border pt-4 space-y-2">
                <div className="flex items-start gap-2 text-sm">
                  <Target className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                  <span className="text-muted-foreground"><span className="font-medium text-foreground">Outcome:</span> Employment and housing transition</span>
                </div>
                <div className="flex items-start gap-2 text-sm">
                  <CheckCircle2 className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                  <span className="text-muted-foreground"><span className="font-medium text-foreground">Purpose:</span> Achieve sustainable independence</span>
                </div>
              </div>
            </div>
          </div>

          <div className="mt-8 text-center">
            <Link to="/model">
              <Button variant="outline" size="lg">
                View Full Operational Model
                <ArrowRight className="w-4 h-4" />
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Development Status */}
      <section className="py-16 lg:py-24 bg-background">
        <div className="container-wide section-padding">
          <div className="max-w-4xl">
            <h2 className="text-3xl lg:text-4xl font-serif font-bold text-foreground mb-6">
              Current Development Phase
            </h2>
            <p className="text-lg text-muted-foreground leading-relaxed mb-8">
              Klear Path is in active pre-development. The following milestones define our 
              current trajectory toward operational launch.
            </p>
            <div className="space-y-4">
              {[
                { label: "501(c)(3) determination received", detail: "Federally recognized public charity" },
                { label: "Board formation underway", detail: "Governance structure in development" },
                { label: "Pre-development capital planning", detail: "Budget modeling and funding strategy" },
                { label: "County alignment conversations scheduled", detail: "Bucks & Montgomery Counties stakeholder engagement" },
                { label: "Phase 1 pilot planning", detail: "Site requirements and operational design" },
              ].map((item, i) => (
                <div key={i} className="flex items-start gap-4 bg-card border border-border rounded-lg p-5">
                  <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <TrendingUp className="w-4 h-4 text-primary" />
                  </div>
                  <div>
                    <p className="font-semibold text-foreground">{item.label}</p>
                    <p className="text-sm text-muted-foreground">{item.detail}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Trust Signals */}
      <section className="py-16 lg:py-20 bg-primary text-primary-foreground">
        <div className="container-wide section-padding">
          <div className="max-w-3xl">
            <h2 className="text-3xl lg:text-4xl font-serif font-bold mb-6">
              Built on Lived Experience + Structured Systems Design
            </h2>
            <p className="text-lg text-primary-foreground/85 leading-relaxed">
              Designed by individuals with firsthand experience navigating system gaps, 
              combined with structured operational planning and workforce integration strategy. 
              This dual foundation ensures programming is both practically informed and 
              institutionally viable.
            </p>
          </div>
        </div>
      </section>

      {/* AI-Assisted Service Coordination */}
      <section className="py-16 lg:py-24 bg-secondary">
        <div className="container-wide section-padding">
          <div className="max-w-4xl">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center">
                <Cpu className="w-6 h-6 text-primary" />
              </div>
              <h2 className="text-3xl lg:text-4xl font-serif font-bold text-foreground">
                AI-Assisted Service Coordination
              </h2>
            </div>
            <p className="text-lg text-muted-foreground leading-relaxed mb-8">
              Klear Path is developing AI-assisted tools that help staff and volunteers coordinate 
              housing stabilization services more efficiently. These systems assist with participant 
              intake documentation, service referrals, grant writing, and impact reporting—so our 
              team can focus more time on direct support.
            </p>
            <p className="text-lg text-muted-foreground leading-relaxed mb-10">
              By combining community partnerships with modern technology, Klear Path aims to create 
              scalable solutions that allow small teams to serve more individuals experiencing 
              housing instability.
            </p>
            <div className="grid sm:grid-cols-2 gap-6">
              <div className="bg-card border border-border rounded-xl p-6 flex items-start gap-4">
                <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
                  <ClipboardList className="w-5 h-5 text-primary" />
                </div>
                <div>
                  <p className="font-semibold text-foreground mb-1">Intake & Documentation</p>
                  <p className="text-sm text-muted-foreground">AI-assisted participant intake and case summary generation</p>
                </div>
              </div>
              <div className="bg-card border border-border rounded-xl p-6 flex items-start gap-4">
                <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
                  <ArrowRight className="w-5 h-5 text-primary" />
                </div>
                <div>
                  <p className="font-semibold text-foreground mb-1">Service Referrals</p>
                  <p className="text-sm text-muted-foreground">Smart matching to employment support, ID recovery, and housing resources</p>
                </div>
              </div>
              <div className="bg-card border border-border rounded-xl p-6 flex items-start gap-4">
                <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
                  <FileSearch className="w-5 h-5 text-primary" />
                </div>
                <div>
                  <p className="font-semibold text-foreground mb-1">Grant Writing Support</p>
                  <p className="text-sm text-muted-foreground">AI-powered drafting and research to accelerate funding applications</p>
                </div>
              </div>
              <div className="bg-card border border-border rounded-xl p-6 flex items-start gap-4">
                <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
                  <BarChart3 className="w-5 h-5 text-primary" />
                </div>
                <div>
                  <p className="font-semibold text-foreground mb-1">Impact Reporting</p>
                  <p className="text-sm text-muted-foreground">Automated outcome tracking and funder-ready report generation</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Tax-Exempt Status */}
      <section className="py-12 lg:py-16 bg-background">
        <div className="container-wide section-padding">
          <div className="max-w-2xl mx-auto text-center">
            <h2 className="text-2xl lg:text-3xl font-serif font-bold text-foreground mb-4">
              Tax-Exempt Status
            </h2>
            <p className="text-muted-foreground leading-relaxed mb-2">
              Klear Path is an IRS-recognized 501(c)(3) public charity.
              Donations are tax-deductible to the fullest extent permitted by law.
            </p>
            <p className="text-sm font-semibold text-foreground mb-6">EIN: 41-3156622</p>
            <a href="/klearpath_501c3.pdf" target="_blank" rel="noopener noreferrer">
              <Button variant="outline" size="lg">
                <FileText className="w-4 h-4" />
                Download IRS Determination Letter
              </Button>
            </a>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 lg:py-24 bg-secondary">
        <div className="container-wide section-padding">
          <div className="max-w-3xl mx-auto text-center">
            <h2 className="text-3xl lg:text-4xl font-serif font-bold text-foreground mb-4">
              Next Steps
            </h2>
            <p className="text-lg text-muted-foreground mb-10 leading-relaxed">
              Klear Path is seeking aligned partners—county agencies, foundations, and 
              institutional funders—to advance structured housing infrastructure in Bucks & Montgomery Counties.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <a href="/klearpath_501c3.pdf" target="_blank" rel="noopener noreferrer">
                <Button size="xl">
                  <FileText className="w-5 h-5" />
                  Download Mission Brief
                </Button>
              </a>
              <Link to="/contact">
                <Button variant="outline" size="xl">
                  <MessageSquare className="w-5 h-5" />
                  Request Strategic Partnership Meeting
                </Button>
              </Link>
            </div>
            <div className="mt-6">
              <Link to="/get-involved" className="inline-flex items-center gap-2 text-primary font-medium hover:underline">
                <Users className="w-4 h-4" />
                Join the Founding 25
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          </div>
        </div>
      </section>
    </Layout>
  );
};

export default Index;
