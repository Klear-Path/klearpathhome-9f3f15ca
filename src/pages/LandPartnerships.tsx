import { Link } from "react-router-dom";
import { Helmet } from "react-helmet-async";
import { Layout } from "@/components/layout/Layout";
import { Button } from "@/components/ui/button";
import { ArrowRight, Gift, FileSignature, Wrench, Building2, Search, Church, ShieldCheck } from "lucide-react";

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
      <title>Land Partnerships | Donate or Lease Land for Housing Stability | Klear Path</title>
      <meta name="description" content="Land can become legacy. Klear Path partners with landowners, faith communities, municipalities, and developers to turn idle land into stability and workforce outcomes." />
      <meta name="keywords" content="land donation nonprofit, donate land for community impact, faith-based land partnerships, redevelopment parcel donation" />
      <link rel="canonical" href="https://klearpathhome.org/land-partnerships" />
    </Helmet>

    <section className="py-16 lg:py-24 bg-primary text-primary-foreground">
      <div className="container-wide section-padding">
        <div className="max-w-3xl">
          <p className="text-primary-foreground/70 font-medium mb-3 tracking-wide uppercase text-sm">Land & Site Partnerships</p>
          <h1 className="text-4xl lg:text-5xl font-serif font-bold mb-6">Land Can Become Legacy</h1>
          <p className="text-xl text-primary-foreground/90 leading-relaxed mb-8">
            Klear Path is exploring donated land, long-term leases, redevelopment parcels, faith-based land partnerships, and public-private site opportunities for future pilot deployment.
          </p>
          <Link to="/contact"><Button variant="hero" size="xl" data-cta="land_inquiry_submit">Submit a Property for Review<ArrowRight className="w-5 h-5" /></Button></Link>
        </div>
      </div>
    </section>

    <section className="py-16 lg:py-24 bg-background">
      <div className="container-wide section-padding">
        <div className="max-w-3xl mb-12">
          <h2 className="text-3xl lg:text-4xl font-serif font-bold text-foreground mb-4">Turn Idle Land Into Stability</h2>
          <p className="text-lg text-muted-foreground">Property partnerships for good — flexible structures designed to help launch a pilot site.</p>
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
        <div className="mt-12 max-w-3xl">
          <h3 className="font-serif text-2xl font-semibold text-foreground mb-3">Property Types We Consider</h3>
          <ul className="grid sm:grid-cols-2 gap-2 text-muted-foreground text-sm">
            <li>• Vacant land</li>
            <li>• Underused municipal property</li>
            <li>• Church or faith-based land</li>
            <li>• Redevelopment parcels</li>
            <li>• Commercial properties suitable for adaptive reuse</li>
            <li>• Donated or discounted property</li>
            <li>• Long-term land lease opportunities</li>
          </ul>
        </div>
      </div>
    </section>

    <section className="py-16 lg:py-24 bg-secondary">
      <div className="container-wide section-padding">
        <div className="max-w-3xl mx-auto text-center">
          <h2 className="text-3xl font-serif font-bold text-foreground mb-4">Site Evaluation Criteria</h2>
          <ul className="text-left bg-card border border-border rounded-xl p-8 space-y-3 text-muted-foreground mb-8">
            <li>• Approximately 5–15 acres in Montgomery County, Bucks County, or the Pottstown regional service area</li>
            <li>• Suitable for micro-village deployment or adaptive reuse of existing structures</li>
            <li>• Donation, ground lease, or public-purpose transfer structures considered</li>
            <li>• Faith-based, municipal, redevelopment authority, and private landowner partnerships welcome</li>
          </ul>
          <div className="flex flex-wrap gap-3 justify-center">
            <Link to="/contact"><Button size="xl" data-cta="land_inquiry_submit">Submit a Property for Review<ArrowRight className="w-5 h-5" /></Button></Link>
            <Link to="/for-counties"><Button variant="outline" size="xl">County & Municipal Partnerships</Button></Link>
            <Link to="/fund-a-pilot"><Button variant="outline" size="xl">Fund a Pilot</Button></Link>
          </div>
          <div className="mt-10 bg-card border border-border rounded-xl p-6 text-left flex gap-3">
            <ShieldCheck className="w-5 h-5 text-primary flex-shrink-0 mt-1" />
            <p className="text-sm text-muted-foreground">
              <strong className="text-foreground">Legal &amp; tax disclaimer:</strong> Klear Path does not provide legal or tax advice. Property owners should consult qualified legal and tax professionals regarding any potential donation, lease, or charitable deduction.
            </p>
          </div>
        </div>
      </div>
    </section>
  </Layout>
);

export default LandPartnerships;