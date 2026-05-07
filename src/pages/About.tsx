import { Link } from "react-router-dom";
import { Layout } from "@/components/layout/Layout";
import { Button } from "@/components/ui/button";
import { Heart, Users, Shield, FileText, ArrowRight, CheckCircle } from "lucide-react";

const About = () => {
  return (
    <Layout>
      {/* Hero */}
      <section className="py-16 lg:py-24 bg-primary text-primary-foreground">
        <div className="container-wide section-padding">
          <div className="max-w-3xl">
            <h1 className="text-4xl lg:text-5xl font-serif font-bold mb-6">
              About Klear Path
            </h1>
            <p className="text-xl text-primary-foreground/90 leading-relaxed">
              We're building Pennsylvania's first integrated housing, safety, and workforce 
              campus—designed with our neighbors experiencing homelessness, not just for them.
            </p>
          </div>
        </div>
      </section>

      {/* Mission & Vision */}
      <section className="py-16 lg:py-24">
        <div className="container-wide section-padding">
          <div className="max-w-4xl mx-auto mb-16 space-y-6">
            <h2 className="text-3xl lg:text-4xl font-serif font-semibold text-foreground">
              Who We Are
            </h2>
            <p className="text-lg text-muted-foreground leading-relaxed">
              Klear Path is a nonprofit organization dedicated to helping individuals overcome
              homelessness, instability, and life-altering hardship through advocacy, housing
              support, resource navigation, and long-term recovery initiatives. From the moment
              someone walks through our doors, they are treated as "homeless no more" — because
              we believe real change begins with dignity, stability, accountability, and belonging.
            </p>
            <p className="text-lg text-muted-foreground leading-relaxed">
              Our vision goes beyond temporary shelter. Klear Path is designed around sustainable
              recovery models that include transitional housing pod communities, individualized
              support systems, life-skills development, resource coordination, mentorship, and
              incentive-based progress programs that reward personal growth, responsibility, and
              forward movement. We aim to help individuals rebuild confidence, independence, and
              purpose while creating a real pathway back into society.
            </p>
            <p className="text-lg text-muted-foreground leading-relaxed">
              What makes Klear Path uniquely different is that it was built from firsthand lived
              experience, not theory. We understand the systemic gaps, emotional toll, and
              practical barriers people face because we have lived them ourselves. Instead of
              offering temporary fixes or one-size-fits-all solutions, we focus on
              relationship-driven support, real-world problem solving, and creating environments
              where people feel seen, valued, and empowered to reclaim their lives.
            </p>
            <p className="text-xl font-serif font-semibold text-primary leading-relaxed border-l-4 border-primary pl-6">
              Klear Path was born from the understanding that a temporary solution will never
              resolve a permanent problem.
            </p>
          </div>

          <div className="grid lg:grid-cols-2 gap-12">
            <div className="bg-card rounded-xl p-8 shadow-soft border border-border">
              <h2 className="font-serif text-2xl font-semibold mb-4 text-foreground">Our Mission</h2>
              <p className="text-muted-foreground leading-relaxed">
                Klear Path creates pathways from crisis to stability by providing integrated 
                housing, safety, and workforce services that treat every community member with 
                dignity while addressing the systemic barriers to permanent independence.
              </p>
            </div>
            <div className="bg-card rounded-xl p-8 shadow-soft border border-border">
              <h2 className="font-serif text-2xl font-semibold mb-4 text-foreground">Our Vision</h2>
              <p className="text-muted-foreground leading-relaxed">
                A community where no neighbor sleeps unsheltered, where stable housing is 
                paired with meaningful work, and where the systems that perpetuate homelessness 
                are replaced with systems that build lasting stability.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Our Approach */}
      <section className="py-16 lg:py-24 bg-secondary">
        <div className="container-wide section-padding">
          <div className="max-w-3xl mx-auto text-center mb-12">
            <h2 className="text-3xl lg:text-4xl font-serif font-semibold text-foreground mb-4">
              Our Approach
            </h2>
            <p className="text-lg text-muted-foreground">
              Dignity-first. Systems-focused. Community-centered.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            <div className="bg-card rounded-xl p-6 shadow-soft border border-border">
              <Heart className="w-10 h-10 text-primary mb-4" />
              <h3 className="font-serif font-semibold text-lg mb-2">Dignity First</h3>
              <p className="text-muted-foreground text-sm">
                We use language and practices that respect the full humanity of every person 
                we serve. Terms like "neighbors" and "community members seeking stability" 
                reflect our belief that housing status doesn't define a person's worth.
              </p>
            </div>
            <div className="bg-card rounded-xl p-6 shadow-soft border border-border">
              <Shield className="w-10 h-10 text-primary mb-4" />
              <h3 className="font-serif font-semibold text-lg mb-2">Systems Focused</h3>
              <p className="text-muted-foreground text-sm">
                Homelessness isn't just about individuals—it's about broken systems. Our 
                integrated model addresses housing, employment, and support services together 
                because these challenges are interconnected.
              </p>
            </div>
            <div className="bg-card rounded-xl p-6 shadow-soft border border-border">
              <Users className="w-10 h-10 text-primary mb-4" />
              <h3 className="font-serif font-semibold text-lg mb-2">Community Centered</h3>
              <p className="text-muted-foreground text-sm">
                We design programs with input from those who've experienced housing instability, 
                not just for them. Their insights shape better solutions.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Leadership */}
      <section className="py-16 lg:py-24">
        <div className="container-wide section-padding">
          <div className="text-center mb-12">
            <h2 className="text-3xl lg:text-4xl font-serif font-semibold text-foreground mb-4">
              Leadership
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Our team brings together lived experience, professional expertise, and deep 
              commitment to our mission.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            {/* Founder */}
            <div className="bg-card rounded-xl p-8 shadow-medium border border-border">
              <div className="w-20 h-20 rounded-full bg-primary/10 flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-serif font-bold text-primary">EM</span>
              </div>
              <h3 className="font-serif text-xl font-semibold text-center mb-1">Erick McKee</h3>
              <p className="text-primary text-center text-sm font-medium mb-4">Founder & Executive Director</p>
              <p className="text-muted-foreground text-sm leading-relaxed">
                Erick founded Klear Path with operational insight drawn from firsthand experience 
                navigating housing instability. This perspective informs every aspect of our 
                model—from the design of our micro-village units to our trauma-informed approach 
                at the Safety Center. He brings a deep understanding of both the challenges our 
                neighbors face and the practical solutions that can make a difference.
              </p>
            </div>

            {/* Program Coordinator */}
            <div className="bg-card rounded-xl p-8 shadow-medium border border-border">
              <div className="w-20 h-20 rounded-full bg-primary/10 flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-serif font-bold text-primary">DM</span>
              </div>
              <h3 className="font-serif text-xl font-semibold text-center mb-1">Dominique McKee</h3>
              <p className="text-primary text-center text-sm font-medium mb-4">Program Coordinator</p>
              <p className="text-muted-foreground text-sm leading-relaxed">
                Dominique oversees day-to-day program operations and resident services, ensuring 
                that Klear Path's vision translates into consistent, high-quality support for 
                every community member we serve. Her focus on relationship-building and 
                individualized care planning helps residents navigate their unique paths to stability.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Governance */}
      <section className="py-16 lg:py-24 bg-accent">
        <div className="container-wide section-padding">
          <div className="max-w-4xl mx-auto">
            <div className="text-center mb-12">
              <FileText className="w-12 h-12 text-primary mx-auto mb-4" />
              <h2 className="text-3xl lg:text-4xl font-serif font-semibold text-foreground mb-4">
                Governance & Accountability
              </h2>
              <p className="text-lg text-muted-foreground">
                Good governance protects our mission and your trust.
              </p>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
              <div className="bg-card rounded-xl p-6 shadow-soft border border-border">
                <h3 className="font-serif font-semibold text-lg mb-3">Board of Directors</h3>
                <p className="text-muted-foreground text-sm mb-4">
                  An independent Board of Directors provides strategic oversight and fiduciary 
                  responsibility. Board members serve without compensation and bring diverse 
                  expertise in nonprofit management, finance, social services, and community 
                  development.
                </p>
                <p className="text-xs text-muted-foreground italic">
                  Board roster available upon request.
                </p>
              </div>

              <div className="bg-card rounded-xl p-6 shadow-soft border border-border">
                <h3 className="font-serif font-semibold text-lg mb-3">Conflict of Interest Policy</h3>
                <p className="text-muted-foreground text-sm">
                  All board members, officers, and key employees are required to disclose 
                  any potential conflicts of interest annually and to recuse themselves from 
                  decisions where a conflict may exist. This policy ensures that all 
                  organizational decisions are made in the best interest of our mission.
                </p>
              </div>

              <div className="bg-card rounded-xl p-6 shadow-soft border border-border">
                <h3 className="font-serif font-semibold text-lg mb-3">Financial Oversight</h3>
                <p className="text-muted-foreground text-sm">
                  The Board's Finance Committee reviews financial statements monthly and 
                  oversees the annual budget process. We maintain clear separation between 
                  operating funds and restricted donations.
                </p>
              </div>

              <div className="bg-card rounded-xl p-6 shadow-soft border border-border">
                <h3 className="font-serif font-semibold text-lg mb-3">Transparency Commitment</h3>
                <p className="text-muted-foreground text-sm">
                  Our IRS Form 990, audited financial statements (when available), and 
                  organizational policies are available to any donor, partner, or community 
                  member upon request.
                </p>
              </div>
            </div>

            <div className="mt-8 bg-card rounded-xl p-6 shadow-soft border border-border">
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                <div>
                  <h3 className="font-semibold mb-1">Request Governance Documents</h3>
                  <p className="text-sm text-muted-foreground">
                    Conflict of interest policy, bylaws, and other documents available upon request.
                  </p>
                </div>
                <Link to="/contact">
                  <Button variant="outline">
                    Contact Us
                    <ArrowRight className="w-4 h-4" />
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Legal Information */}
      <section className="py-16 lg:py-20">
        <div className="container-wide section-padding text-center">
          <h2 className="text-2xl font-serif font-semibold text-foreground mb-6">
            Legal Information
          </h2>
          <div className="bg-secondary rounded-xl p-6 max-w-lg mx-auto">
            <p className="font-medium text-foreground mb-2">Klear Path Home, Inc.</p>
            <p className="text-muted-foreground text-sm mb-2">
              A federally recognized 501(c)(3) public charity focused on permanent village-based reintegration campuses
            </p>
            <p className="text-muted-foreground text-sm">
              <strong>EIN:</strong> 41-3156622
            </p>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-16 lg:py-20 bg-primary text-primary-foreground">
        <div className="container-wide section-padding text-center">
          <h2 className="text-3xl lg:text-4xl font-serif font-semibold mb-4">
            Join Our Mission
          </h2>
          <p className="text-xl text-primary-foreground/90 max-w-2xl mx-auto mb-8">
            Whether through donation, volunteering, or partnership—your support helps build 
            pathways to stability for our neighbors.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/donate">
              <Button variant="hero" size="lg">
                <Heart className="w-4 h-4" />
                Donate Now
              </Button>
            </Link>
            <Link to="/get-involved">
              <Button variant="hero-outline" size="lg">
                Get Involved
              </Button>
            </Link>
          </div>
        </div>
      </section>
    </Layout>
  );
};

export default About;
