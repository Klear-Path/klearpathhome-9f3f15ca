import { Link } from "react-router-dom";
import { Layout } from "@/components/layout/Layout";
import { Button } from "@/components/ui/button";
import { Shield, Home, Briefcase, Sun, Users, Clock, Heart, ArrowRight, CheckCircle } from "lucide-react";

const TheModel = () => {
  return (
    <Layout>
      {/* Hero */}
      <section className="py-16 lg:py-24 bg-primary text-primary-foreground">
        <div className="container-wide section-padding">
          <div className="max-w-3xl">
            <h1 className="text-4xl lg:text-5xl font-serif font-bold mb-6">
              The Klear Path Model
            </h1>
            <p className="text-xl text-primary-foreground/90 leading-relaxed">
              An integrated approach that addresses immediate crisis, provides dignified 
              transitional housing, and builds pathways to permanent stability—all in one campus.
            </p>
          </div>
        </div>
      </section>

      {/* Why Integrated */}
      <section className="py-16 lg:py-24">
        <div className="container-wide section-padding">
          <div className="max-w-3xl mx-auto text-center mb-12">
            <h2 className="text-3xl lg:text-4xl font-serif font-semibold text-foreground mb-4">
              Why an Integrated Model?
            </h2>
            <p className="text-lg text-muted-foreground leading-relaxed">
              Traditional approaches often treat homelessness as a single problem with a single 
              solution. But our neighbors experiencing housing instability face interconnected 
              challenges—and they deserve interconnected solutions.
            </p>
          </div>

          <div className="grid lg:grid-cols-3 gap-8">
            <div className="bg-card p-6 rounded-xl shadow-soft border border-border">
              <div className="text-primary font-serif text-5xl font-bold mb-2">1</div>
              <h3 className="font-serif text-xl font-semibold mb-3">Safety First</h3>
              <p className="text-muted-foreground">
                People in crisis can't plan for the future. Our 24/7 Safety Center provides 
                immediate refuge so individuals can stabilize before taking next steps.
              </p>
            </div>
            <div className="bg-card p-6 rounded-xl shadow-soft border border-border">
              <div className="text-primary font-serif text-5xl font-bold mb-2">2</div>
              <h3 className="font-serif text-xl font-semibold mb-3">Stable Housing</h3>
              <p className="text-muted-foreground">
                Private, dignified housing gives residents the foundation they need to focus 
                on recovery, job training, and rebuilding their lives.
              </p>
            </div>
            <div className="bg-card p-6 rounded-xl shadow-soft border border-border">
              <div className="text-primary font-serif text-5xl font-bold mb-2">3</div>
              <h3 className="font-serif text-xl font-semibold mb-3">Economic Pathway</h3>
              <p className="text-muted-foreground">
                Workforce development creates lasting independence. We don't just shelter—we 
                equip residents with marketable skills and job placement support.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* 24/7 Safety Center */}
      <section className="py-16 lg:py-24 bg-secondary">
        <div className="container-wide section-padding">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <div className="w-16 h-16 rounded-xl bg-primary/10 flex items-center justify-center mb-6">
                <Shield className="w-8 h-8 text-primary" />
              </div>
              <h2 className="text-3xl lg:text-4xl font-serif font-semibold text-foreground mb-4">
                24/7 Safety Center
              </h2>
              <p className="text-lg text-muted-foreground leading-relaxed mb-6">
                The first point of contact for community members in crisis. Open around the 
                clock, our Safety Center provides a welcoming environment where individuals 
                can find immediate refuge and begin their journey toward stability.
              </p>
              <ul className="space-y-3">
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-primary mt-0.5 flex-shrink-0" />
                  <span className="text-foreground">Safe, secure space open 24 hours a day, 7 days a week</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-primary mt-0.5 flex-shrink-0" />
                  <span className="text-foreground">Hot meals, showers, and laundry facilities</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-primary mt-0.5 flex-shrink-0" />
                  <span className="text-foreground">On-site case management and service navigation</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-primary mt-0.5 flex-shrink-0" />
                  <span className="text-foreground">Connection to medical care and mental health services</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-primary mt-0.5 flex-shrink-0" />
                  <span className="text-foreground">Low-barrier entry with trauma-informed approach</span>
                </li>
              </ul>
            </div>
            <div className="bg-card rounded-2xl p-8 shadow-medium border border-border">
              <div className="flex items-center gap-3 mb-4">
                <Clock className="w-6 h-6 text-primary" />
                <span className="font-semibold text-lg">Hours of Operation</span>
              </div>
              <p className="text-3xl font-serif font-bold text-primary mb-6">
                24 Hours a Day<br />7 Days a Week<br />365 Days a Year
              </p>
              <p className="text-muted-foreground">
                Crisis doesn't follow a schedule. Neither do we. Our neighbors can access 
                safety and support whenever they need it.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Micro-Village Housing */}
      <section className="py-16 lg:py-24">
        <div className="container-wide section-padding">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div className="order-2 lg:order-1 bg-accent rounded-2xl p-8">
              <h3 className="font-serif text-2xl font-semibold mb-6 text-foreground">Phase 1 Specifications</h3>
              <div className="grid grid-cols-2 gap-6">
                <div>
                  <p className="text-4xl font-serif font-bold text-primary">25</p>
                  <p className="text-muted-foreground">Private housing pods</p>
                </div>
                <div>
                  <p className="text-4xl font-serif font-bold text-primary">~120</p>
                  <p className="text-muted-foreground">Square feet per unit</p>
                </div>
                <div>
                  <p className="text-4xl font-serif font-bold text-primary">100%</p>
                  <p className="text-muted-foreground">Climate controlled</p>
                </div>
                <div>
                  <p className="text-4xl font-serif font-bold text-primary">24/7</p>
                  <p className="text-muted-foreground">On-site support staff</p>
                </div>
              </div>
            </div>
            <div className="order-1 lg:order-2">
              <div className="w-16 h-16 rounded-xl bg-primary/10 flex items-center justify-center mb-6">
                <Home className="w-8 h-8 text-primary" />
              </div>
              <h2 className="text-3xl lg:text-4xl font-serif font-semibold text-foreground mb-4">
                Micro-Village Housing
              </h2>
              <p className="text-lg text-muted-foreground leading-relaxed mb-6">
                Transitional housing shouldn't mean sacrificing dignity. Our micro-village 
                provides private, secure pod-style units where residents can rest, recover, 
                and focus on their next steps—without the stress of congregate shelters.
              </p>
              <ul className="space-y-3">
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-primary mt-0.5 flex-shrink-0" />
                  <span className="text-foreground">Individual locking units for privacy and security</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-primary mt-0.5 flex-shrink-0" />
                  <span className="text-foreground">Shared community facilities including kitchen and bathrooms</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-primary mt-0.5 flex-shrink-0" />
                  <span className="text-foreground">Pet-friendly options for residents with animal companions</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-primary mt-0.5 flex-shrink-0" />
                  <span className="text-foreground">Integration with case management and workforce programs</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Workforce Pathway */}
      <section className="py-16 lg:py-24 bg-primary text-primary-foreground">
        <div className="container-wide section-padding">
          <div className="max-w-3xl mx-auto text-center mb-12">
            <div className="w-16 h-16 rounded-xl bg-primary-foreground/20 flex items-center justify-center mx-auto mb-6">
              <Briefcase className="w-8 h-8 text-primary-foreground" />
            </div>
            <h2 className="text-3xl lg:text-4xl font-serif font-semibold mb-4">
              Workforce & Skills Pathway
            </h2>
            <p className="text-xl text-primary-foreground/90 leading-relaxed">
              Shelter is temporary. Skills are permanent. Our workforce development program 
              equips residents with marketable skills in high-demand fields—with a special 
              focus on sustainable energy careers.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-primary-foreground/10 rounded-xl p-6 text-center">
              <Sun className="w-10 h-10 mx-auto mb-4 text-primary-foreground" />
              <h3 className="font-serif font-semibold text-lg mb-2">Solar Installation</h3>
              <p className="text-primary-foreground/80 text-sm">
                Hands-on training in residential and commercial solar panel installation.
              </p>
            </div>
            <div className="bg-primary-foreground/10 rounded-xl p-6 text-center">
              <Briefcase className="w-10 h-10 mx-auto mb-4 text-primary-foreground" />
              <h3 className="font-serif font-semibold text-lg mb-2">Green Building</h3>
              <p className="text-primary-foreground/80 text-sm">
                Energy efficiency, weatherization, and sustainable construction techniques.
              </p>
            </div>
            <div className="bg-primary-foreground/10 rounded-xl p-6 text-center">
              <Users className="w-10 h-10 mx-auto mb-4 text-primary-foreground" />
              <h3 className="font-serif font-semibold text-lg mb-2">Job Placement</h3>
              <p className="text-primary-foreground/80 text-sm">
                Connections to local employers and ongoing career support services.
              </p>
            </div>
            <div className="bg-primary-foreground/10 rounded-xl p-6 text-center">
              <Heart className="w-10 h-10 mx-auto mb-4 text-primary-foreground" />
              <h3 className="font-serif font-semibold text-lg mb-2">Life Skills</h3>
              <p className="text-primary-foreground/80 text-sm">
                Financial literacy, interview prep, and professional development.
              </p>
            </div>
          </div>

          <div className="mt-12 text-center">
            <p className="text-primary-foreground/70 mb-6">
              Our goal: residents graduate with certifications, job offers, and savings—ready 
              for permanent housing and lasting independence.
            </p>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-16 lg:py-20">
        <div className="container-wide section-padding text-center">
          <h2 className="text-3xl lg:text-4xl font-serif font-semibold text-foreground mb-4">
            Help Us Build This Vision
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto mb-8">
            The Klear Path model is ready. With land and community support, we can begin 
            construction on Pennsylvania's first integrated housing and workforce campus.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/partners">
              <Button size="lg">
                Partner With Us
                <ArrowRight className="w-4 h-4" />
              </Button>
            </Link>
            <Link to="/donate">
              <Button variant="outline" size="lg">
                <Heart className="w-4 h-4" />
                Support Our Mission
              </Button>
            </Link>
          </div>
        </div>
      </section>
    </Layout>
  );
};

export default TheModel;
