import { Link } from "react-router-dom";
import { useEffect } from "react";
import { Helmet } from "react-helmet-async";
import { Layout } from "@/components/layout/Layout";
import { Button } from "@/components/ui/button";
import { Heart, Home, ArrowRight } from "lucide-react";

declare global {
  interface Window {
    gtag?: (...args: any[]) => void;
  }
}

const ThankYou = () => {
  useEffect(() => {
    if (typeof window !== "undefined" && typeof window.gtag === "function") {
      window.gtag("event", "conversion", {
        send_to: "AW-18192459416/gQELCOC-tbccEJjN6-JD",
      });
    }
  }, []);

  return (
  <Layout>
    <Helmet>
      <title>Thank You for Your Gift | Klear Path</title>
      <meta name="description" content="Thank you for supporting Klear Path Home, Inc. Your contribution directly funds housing stability and workforce programs in Bucks & Montgomery Counties." />
      <meta name="robots" content="noindex" />
    </Helmet>

    <section className="py-24 lg:py-32 bg-primary text-primary-foreground">
      <div className="container-wide section-padding text-center max-w-3xl mx-auto">
        <div className="w-20 h-20 rounded-full bg-primary-foreground/15 flex items-center justify-center mx-auto mb-8">
          <Heart className="w-10 h-10" />
        </div>
        <h1 className="text-4xl lg:text-6xl font-serif font-bold mb-6">Thank You</h1>
        <p className="text-xl lg:text-2xl text-primary-foreground/90 leading-relaxed mb-4">
          Your generosity makes the next pathway home possible.
        </p>
        <p className="text-lg text-primary-foreground/80 leading-relaxed">
          A confirmation receipt from Stripe will arrive in your inbox shortly. Klear Path Home, Inc.
          is a federally recognized 501(c)(3) public charity (EIN 41-3156622); your gift is
          tax-deductible to the fullest extent permitted by law.
        </p>
      </div>
    </section>

    <section className="py-16 lg:py-20">
      <div className="container-wide section-padding max-w-4xl mx-auto">
        <h2 className="text-3xl font-serif font-semibold text-foreground mb-6 text-center">
          What Your Contribution Does
        </h2>
        <p className="text-lg text-muted-foreground leading-relaxed text-center mb-10 max-w-2xl mx-auto">
          Every dollar entrusted to Klear Path strengthens a coordinated system of housing
          stabilization, workforce development, and dignified service for our neighbors working
          toward lasting independence.
        </p>
        <div className="grid sm:grid-cols-3 gap-6">
          <div className="bg-card border border-border rounded-xl p-6 text-center">
            <p className="font-serif font-bold text-2xl text-primary mb-2">Housing</p>
            <p className="text-sm text-muted-foreground">Funds stabilization beds, micro-village pods, and on-site case management.</p>
          </div>
          <div className="bg-card border border-border rounded-xl p-6 text-center">
            <p className="font-serif font-bold text-2xl text-primary mb-2">Workforce</p>
            <p className="text-sm text-muted-foreground">Provides job-training materials, certifications, and employer placement support.</p>
          </div>
          <div className="bg-card border border-border rounded-xl p-6 text-center">
            <p className="font-serif font-bold text-2xl text-primary mb-2">Coordination</p>
            <p className="text-sm text-muted-foreground">Powers AI-assisted intake and outcome reporting so more neighbors are served.</p>
          </div>
        </div>
      </div>
    </section>

    <section className="py-16 bg-secondary">
      <div className="container-wide section-padding text-center">
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link to="/">
            <Button size="lg"><Home className="w-4 h-4" /> Return Home</Button>
          </Link>
          <Link to="/housing-stabilization-model">
            <Button variant="outline" size="lg">Explore Our Model<ArrowRight className="w-4 h-4" /></Button>
          </Link>
        </div>
        <p className="text-sm text-muted-foreground mt-8">
          Questions about your gift? Email <a href="mailto:info@klearpathhome.org" className="underline">info@klearpathhome.org</a>.
        </p>
      </div>
    </section>
  </Layout>
  );
};

export default ThankYou;