import { Link } from "react-router-dom";
import { Helmet } from "react-helmet-async";
import { Layout } from "@/components/layout/Layout";
import { Button } from "@/components/ui/button";
import { ArrowRight, CheckCircle, Users, Building2, Cpu, Handshake, Target, TrendingUp } from "lucide-react";

const HousingStabilizationModel = () => {
  return (
    <Layout>
      <Helmet>
        <title>Housing Stabilization Model | Klear Path</title>
        <meta name="description" content="Klear Path's scalable housing stabilization model combines service coordination, community partnerships, and AI-assisted technology to create lasting solutions for homelessness prevention." />
        <meta name="keywords" content="housing stabilization programs, homelessness solutions nonprofit, innovative housing programs, housing stability services, community housing partnerships" />
      </Helmet>

      {/* Hero */}
      <section className="py-16 lg:py-24 bg-primary text-primary-foreground">
        <div className="container-wide section-padding">
          <div className="max-w-3xl">
            <p className="text-primary-foreground/70 font-medium mb-3 tracking-wide uppercase text-sm">
              Our Approach
            </p>
            <h1 className="text-4xl lg:text-5xl font-serif font-bold mb-6">
              A Scalable Model for Housing Stabilization
            </h1>
            <p className="text-xl text-primary-foreground/90 leading-relaxed">
              Klear Path is building a coordinated approach to housing stabilization that combines
              direct services, community partnerships, and technology-assisted coordination.
            </p>
          </div>
        </div>
      </section>

      {/* The Challenge */}
      <section className="py-16 lg:py-24">
        <div className="container-wide section-padding">
          <div className="max-w-4xl">
            <h2 className="text-3xl lg:text-4xl font-serif font-bold text-foreground mb-6">
              The Challenge
            </h2>
            <p className="text-lg text-muted-foreground leading-relaxed mb-6">
              Housing instability remains a growing challenge across communities nationwide. While many
              programs address immediate needs through emergency shelters and short-term assistance, few
              offer the long-term, coordinated solutions necessary to help individuals achieve lasting stability.
            </p>
            <p className="text-lg text-muted-foreground leading-relaxed">
              Fragmented services, limited coordination between providers, and a lack of data-driven
              approaches mean that individuals often cycle through the same systems without achieving
              meaningful, sustainable outcomes. Communities need innovative housing programs that connect
              the dots between housing, employment, and supportive services.
            </p>
          </div>
        </div>
      </section>

      {/* The Klear Path Model — Three Pillars */}
      <section className="py-16 lg:py-24 bg-secondary">
        <div className="container-wide section-padding">
          <div className="mb-12">
            <h2 className="text-3xl lg:text-4xl font-serif font-bold text-foreground mb-4">
              The Klear Path Model
            </h2>
            <p className="text-lg text-muted-foreground max-w-3xl">
              Our housing stabilization framework is built on three interconnected pillars that
              work together to create comprehensive, lasting outcomes.
            </p>
          </div>

          <div className="grid lg:grid-cols-3 gap-8">
            {/* Pillar 1 */}
            <div className="bg-card rounded-xl border border-border p-8">
              <div className="w-14 h-14 rounded-xl bg-primary/10 flex items-center justify-center mb-5">
                <Users className="w-7 h-7 text-primary" />
              </div>
              <h3 className="text-xl font-serif font-semibold text-foreground mb-3">
                Service Coordination
              </h3>
              <p className="text-muted-foreground leading-relaxed mb-4">
                Connecting individuals with housing resources, employment pathways, identification
                recovery, and supportive services through a single, coordinated point of access.
              </p>
              <ul className="space-y-2">
                <li className="flex items-start gap-2 text-sm text-muted-foreground">
                  <CheckCircle className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                  <span>Housing resource navigation</span>
                </li>
                <li className="flex items-start gap-2 text-sm text-muted-foreground">
                  <CheckCircle className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                  <span>Employment pathway development</span>
                </li>
                <li className="flex items-start gap-2 text-sm text-muted-foreground">
                  <CheckCircle className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                  <span>ID recovery and vital documents</span>
                </li>
                <li className="flex items-start gap-2 text-sm text-muted-foreground">
                  <CheckCircle className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                  <span>Behavioral health and wellness referrals</span>
                </li>
              </ul>
            </div>

            {/* Pillar 2 */}
            <div className="bg-card rounded-xl border border-border p-8">
              <div className="w-14 h-14 rounded-xl bg-primary/10 flex items-center justify-center mb-5">
                <Handshake className="w-7 h-7 text-primary" />
              </div>
              <h3 className="text-xl font-serif font-semibold text-foreground mb-3">
                Community Partnerships
              </h3>
              <p className="text-muted-foreground leading-relaxed mb-4">
                Working with local organizations, businesses, and service providers to align resources
                and increase community-wide impact on housing stability.
              </p>
              <ul className="space-y-2">
                <li className="flex items-start gap-2 text-sm text-muted-foreground">
                  <CheckCircle className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                  <span>Local nonprofit collaboration</span>
                </li>
                <li className="flex items-start gap-2 text-sm text-muted-foreground">
                  <CheckCircle className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                  <span>Business and employer engagement</span>
                </li>
                <li className="flex items-start gap-2 text-sm text-muted-foreground">
                  <CheckCircle className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                  <span>Government agency coordination</span>
                </li>
                <li className="flex items-start gap-2 text-sm text-muted-foreground">
                  <CheckCircle className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                  <span>Resource alignment and shared outcomes</span>
                </li>
              </ul>
            </div>

            {/* Pillar 3 */}
            <div className="bg-card rounded-xl border border-border p-8">
              <div className="w-14 h-14 rounded-xl bg-primary/10 flex items-center justify-center mb-5">
                <Cpu className="w-7 h-7 text-primary" />
              </div>
              <h3 className="text-xl font-serif font-semibold text-foreground mb-3">
                Technology-Assisted Coordination
              </h3>
              <p className="text-muted-foreground leading-relaxed mb-4">
                Klear Path uses AI-assisted tools to help streamline intake documentation, service
                coordination, and program reporting so staff can spend more time supporting individuals directly.
              </p>
              <ul className="space-y-2">
                <li className="flex items-start gap-2 text-sm text-muted-foreground">
                  <CheckCircle className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                  <span>AI-assisted intake documentation</span>
                </li>
                <li className="flex items-start gap-2 text-sm text-muted-foreground">
                  <CheckCircle className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                  <span>Automated service referral matching</span>
                </li>
                <li className="flex items-start gap-2 text-sm text-muted-foreground">
                  <CheckCircle className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                  <span>Grant writing support tools</span>
                </li>
                <li className="flex items-start gap-2 text-sm text-muted-foreground">
                  <CheckCircle className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                  <span>Automated impact and program reporting</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Why This Approach Works */}
      <section className="py-16 lg:py-24">
        <div className="container-wide section-padding">
          <div className="max-w-4xl">
            <h2 className="text-3xl lg:text-4xl font-serif font-bold text-foreground mb-8">
              Why This Approach Works
            </h2>
            <div className="grid sm:grid-cols-2 gap-6">
              <div className="flex items-start gap-4 bg-accent rounded-xl p-6">
                <Target className="w-8 h-8 text-primary flex-shrink-0" />
                <div>
                  <p className="font-semibold text-foreground mb-1">Reduces Fragmentation</p>
                  <p className="text-sm text-muted-foreground">Coordinated services eliminate gaps and duplication, ensuring individuals receive comprehensive support.</p>
                </div>
              </div>
              <div className="flex items-start gap-4 bg-accent rounded-xl p-6">
                <TrendingUp className="w-8 h-8 text-primary flex-shrink-0" />
                <div>
                  <p className="font-semibold text-foreground mb-1">Supports Long-Term Stability</p>
                  <p className="text-sm text-muted-foreground">Employment pathways and workforce development create sustainable independence beyond temporary housing.</p>
                </div>
              </div>
              <div className="flex items-start gap-4 bg-accent rounded-xl p-6">
                <Cpu className="w-8 h-8 text-primary flex-shrink-0" />
                <div>
                  <p className="font-semibold text-foreground mb-1">Improves Program Outcomes</p>
                  <p className="text-sm text-muted-foreground">Data tracking and reporting enable evidence-based decisions and continuous program improvement.</p>
                </div>
              </div>
              <div className="flex items-start gap-4 bg-accent rounded-xl p-6">
                <Handshake className="w-8 h-8 text-primary flex-shrink-0" />
                <div>
                  <p className="font-semibold text-foreground mb-1">Maximizes Community Resources</p>
                  <p className="text-sm text-muted-foreground">Partnerships align existing resources for greater collective impact across organizations.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Vision */}
      <section className="py-16 lg:py-24 bg-primary text-primary-foreground">
        <div className="container-wide section-padding">
          <div className="max-w-3xl">
            <h2 className="text-3xl lg:text-4xl font-serif font-bold mb-6">
              Our Vision
            </h2>
            <p className="text-xl text-primary-foreground/90 leading-relaxed mb-6">
              Klear Path aims to develop a scalable model that communities across Pennsylvania
              and beyond can implement to coordinate housing stabilization services more effectively.
            </p>
            <p className="text-lg text-primary-foreground/80 leading-relaxed">
              By proving this coordinated approach in Bucks and Montgomery Counties, we are building
              a replicable framework that demonstrates how small nonprofit teams can serve significantly
              more individuals experiencing housing instability—while maintaining high-quality, compassionate support.
            </p>
          </div>
        </div>
      </section>

      {/* Partner With Klear Path */}
      <section className="py-16 lg:py-24">
        <div className="container-wide section-padding">
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-3xl lg:text-4xl font-serif font-bold text-foreground mb-6">
              Partner With Klear Path
            </h2>
            <p className="text-lg text-muted-foreground mb-10 max-w-2xl mx-auto">
              We invite organizations that share our commitment to housing stability to explore
              partnership opportunities.
            </p>

            <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
              <div className="bg-card rounded-xl p-6 border border-border shadow-soft text-center">
                <Building2 className="w-8 h-8 text-primary mx-auto mb-3" />
                <h3 className="font-serif font-semibold mb-2">Foundations</h3>
                <p className="text-sm text-muted-foreground">Grant funding and strategic support</p>
              </div>
              <div className="bg-card rounded-xl p-6 border border-border shadow-soft text-center">
                <Building2 className="w-8 h-8 text-primary mx-auto mb-3" />
                <h3 className="font-serif font-semibold mb-2">Corporate Sponsors</h3>
                <p className="text-sm text-muted-foreground">CSR programs and employee engagement</p>
              </div>
              <div className="bg-card rounded-xl p-6 border border-border shadow-soft text-center">
                <Users className="w-8 h-8 text-primary mx-auto mb-3" />
                <h3 className="font-serif font-semibold mb-2">Community Orgs</h3>
                <p className="text-sm text-muted-foreground">Service coordination and referrals</p>
              </div>
              <div className="bg-card rounded-xl p-6 border border-border shadow-soft text-center">
                <Building2 className="w-8 h-8 text-primary mx-auto mb-3" />
                <h3 className="font-serif font-semibold mb-2">Local Government</h3>
                <p className="text-sm text-muted-foreground">Policy alignment and public resources</p>
              </div>
            </div>

            <Link to="/contact">
              <Button size="xl">
                Contact Us to Explore Partnership
                <ArrowRight className="w-5 h-5" />
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Download */}
      <section className="py-16 lg:py-20 bg-secondary">
        <div className="container-wide section-padding text-center">
          <h2 className="text-3xl font-serif font-semibold text-foreground mb-4">
            Download Our Partnership Overview
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto mb-8">
            Share our housing stabilization model with your organization's decision-makers.
          </p>
          <a href="/KlearPath_Partnership_Overview.pdf" target="_blank" rel="noopener noreferrer">
            <Button size="lg">
              Download Partnership Overview
              <ArrowRight className="w-4 h-4" />
            </Button>
          </a>
        </div>
      </section>
    </Layout>
  );
};

export default HousingStabilizationModel;
