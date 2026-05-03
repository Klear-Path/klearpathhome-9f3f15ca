import { Link } from "react-router-dom";
import { Helmet } from "react-helmet-async";
import { Layout } from "@/components/layout/Layout";
import { Button } from "@/components/ui/button";
import { ArrowRight, Gift, FileSignature, Wrench, Building2, Search, Church } from "lucide-react";

const options = [
  { icon: Gift, title: "Donate Land", desc: "Transfer parcels for permanent public-purpose use with potential tax benefit." },
  { icon: FileSignature, title: "Lease Land", desc: "Long-term ground lease structures that retain ownership while enabling deployment." },
  { icon: Wrench, title: "Sponsor Site Preparation", desc: "Underwrite grading, utilities, or infrastructure to accelerate pilot launch." },
  { icon: Building2, title: "Partner on Redevelopment", desc: "Reposition vacant or underutilized buildings into stabilization housing." },
  { icon: Search, title: "Offer Property for Evaluation", desc: "Submit a parcel for site review, suitability analysis, and feasibility scoping." },
  { icon: Church, title: "Faith-Based Land Partnerships", desc: "Activate underused congregation property as a launchpad for community impact." },
];

const LandPartnerships = () => (
  <Layout>
    <Helmet>
      <title>Land Partnerships | Donate or Lease Land | Klear Path</title>
      <meta name="description" content="Klear Path partners with landowners, churches, municipalities, and developers to convert idle land into housing stability and workforce outcomes." />
    </Helmet>

    <section className="py-16 lg:py-24 bg-primary text-primary-foreground">
      <div className="container-wide section-padding">
        <div className="max-w-3xl">
          <p className="text-primary-foreground/70 font-medium mb-3 tracking-wide uppercase text-sm">Land & Site Partnerships</p>
          <h1 className="text-4xl lg:text-5xl font-serif font-bold mb-6">Idle Land Can Become Active Hope</h1>
          <p className="text-xl text-primary-foreground/90 leading-relaxed mb-8">
            Your land can become a launchpad for stability, employment, and generational change. Klear Path partners with landowners, faith communities, municipalities, and developers to deploy pilot housing stabilization sites.
          </p>
          <Link to="/contact"><Button variant="hero" size="xl">Donate or Offer Land<ArrowRight className="w-5 h-5" /></Button></Link>
        </div>
      </div>
    </section>

    <section className="py-16 lg:py-24 bg-background">
      <div className="container-wide section-padding">
        <div className="max-w-3xl mb-12">
          <h2 className="text-3xl lg:text-4xl font-serif font-bold text-foreground mb-4">Partnership Options</h2>
          <p className="text-lg text-muted-foreground">Flexible structures designed to meet landowners where they are.</p>
        </div>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {options.map((o) => (
            <div key={o.title} className="bg-card border border-border rounded-xl p-6">
              <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                <o.icon className="w-6 h-6 text-primary" />
              </div>
              <h3 className="font-serif text-lg font-semibold text-foreground mb-2">{o.title}</h3>
              <p className="text-sm text-muted-foreground leading-relaxed">{o.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>

    <section className="py-16 lg:py-24 bg-secondary">
      <div className="container-wide section-padding">
        <div className="max-w-3xl mx-auto text-center">
          <h2 className="text-3xl font-serif font-bold text-foreground mb-4">What We're Looking For</h2>
          <ul className="text-left bg-card border border-border rounded-xl p-8 space-y-3 text-muted-foreground mb-8">
            <li>• Approximately 5–15 acres in Bucks County, Montgomery County, or the Pottstown regional service area</li>
            <li>• Suitable for micro-village deployment or adaptive reuse of existing structures</li>
            <li>• Donation, ground lease, or public-purpose transfer structures considered</li>
            <li>• Faith-based, municipal, redevelopment authority, and private landowner partnerships welcome</li>
          </ul>
          <Link to="/contact"><Button size="xl">Submit a Site for Review<ArrowRight className="w-5 h-5" /></Button></Link>
        </div>
      </div>
    </section>
  </Layout>
);

export default LandPartnerships;