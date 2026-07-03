import { useState } from "react";
import { Link } from "react-router-dom";
import { Helmet } from "react-helmet-async";
import { Layout } from "@/components/layout/Layout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useToast } from "@/hooks/use-toast";
import { supabase } from "@/integrations/supabase/client";
import { Heart, Shield, CheckCircle, CreditCard, Gift, ArrowRight, DollarSign, Handshake, Repeat, Coffee, Briefcase, Truck, FileText, BarChart3, Building2, Users } from "lucide-react";
import { EmailCapture } from "@/components/EmailCapture";

const suggestedAmounts = [25, 100, 500, 1000, 2500, 10000];

const impactTiers = [
  { amt: "$25", desc: "Helps provide immediate food, hygiene, and stabilization support." },
  { amt: "$100", desc: "Supports participant readiness, documentation help, and transportation planning." },
  { amt: "$500", desc: "Helps fund workforce preparation and job-readiness support." },
  { amt: "$2,500", desc: "Supports one participant's stabilization-to-employment pathway." },
  { amt: "$10,000", desc: "Helps anchor a pilot cohort." },
];

const allocations = [
  { icon: Shield, t: "Stabilization Support" },
  { icon: Briefcase, t: "Workforce Readiness" },
  { icon: Truck, t: "Transportation Planning" },
  { icon: FileText, t: "Documentation Support" },
  { icon: BarChart3, t: "Participant Tracking" },
  { icon: Building2, t: "Pilot Development" },
  { icon: Users, t: "Community Partnerships" },
];

const Donate = () => {
  const { toast } = useToast();
  const [amount, setAmount] = useState<string>("100");
  const [email, setEmail] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleDonate = async () => {
    const numAmount = parseFloat(amount);
    if (!numAmount || numAmount < 1) {
      toast({ title: "Please enter an amount of at least $1.", variant: "destructive" });
      return;
    }
    setIsLoading(true);
    try {
      if (typeof window !== "undefined" && (window as any).gtag) {
        (window as any).gtag("event", "donation_click", { amount: numAmount });
      }
      const { data, error } = await supabase.functions.invoke("create-donation", {
        body: { amount: numAmount, email: email || undefined },
      });
      if (error) throw error;
      if (data?.url) window.location.href = data.url;
    } catch (err: any) {
      toast({ title: "Something went wrong", description: err.message, variant: "destructive" });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Layout>
      <Helmet>
        <title>Donate Today | Give Stability Before the System Asks Questions | Klear Path</title>
        <meta name="description" content="Support Klear Path with a tax-deductible gift. Your donation funds dignity-first stabilization, workforce readiness, and pathways from crisis to independence." />
        <meta name="keywords" content="donate to housing stability nonprofit, support housing instability solutions, workforce reintegration nonprofit, homelessness prevention support, dignity-first support" />
        <link rel="canonical" href="https://klearpathhome.org/donate" />
      </Helmet>

      <section className="py-16 lg:py-24 bg-primary text-primary-foreground" data-page="donate">
        <div className="container-wide section-padding">
          <div className="max-w-4xl">
            <p className="uppercase tracking-wider text-primary-foreground/70 text-xs font-semibold mb-4">
              Secure giving • 501(c)(3) nonprofit • EIN 41-3156622
            </p>
            <h1 className="text-4xl lg:text-6xl font-serif font-bold mb-6">
              Give Stability Before the System Asks Questions
            </h1>
            <p className="text-xl text-primary-foreground/90 leading-relaxed max-w-3xl mb-8">
              Klear Path starts with dignity: a meal, a drink, a safe moment, and a path toward housing stability, employment, and long-term independence.
            </p>
            <div className="flex flex-wrap gap-3">
              <a href="#give" data-cta="donation_click"><Button variant="hero" size="xl">Donate Today<ArrowRight className="w-5 h-5" /></Button></a>
              <a href="#give" data-cta="donation_click"><Button variant="hero-outline" size="xl">Help Stability Start on Day One</Button></a>
            </div>
          </div>
        </div>
      </section>

      <section id="give" className="py-16 lg:py-24">
        <div className="container-wide section-padding">
          <div className="max-w-3xl mb-10">
            <p className="text-primary font-medium mb-3 tracking-wide uppercase text-sm">Your Gift Moves Someone From Crisis Toward Stability</p>
            <h2 className="text-3xl lg:text-4xl font-serif font-bold text-foreground">Every gift funds a real step on the path.</h2>
          </div>
          <div className="grid lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2">
              <div className="bg-card rounded-2xl shadow-medium border border-border overflow-hidden">
                <div className="bg-primary/5 px-6 py-4 border-b border-border flex items-center justify-between gap-4 flex-wrap">
                  <div>
                    <p className="text-xs uppercase tracking-wider text-primary font-semibold mb-1">Recommended</p>
                    <h2 className="font-serif text-2xl font-semibold text-foreground">
                      Become Part Of Someone's Path Forward
                    </h2>
                  </div>
                  <div className="inline-flex items-center gap-2 rounded-full bg-primary/10 px-4 py-2 text-primary text-sm font-semibold">
                    <Repeat className="w-4 h-4" /> Monthly support is best
                  </div>
                </div>
                <div className="p-8 lg:p-12 space-y-8">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground mb-3 flex items-center gap-2">
                      <Gift className="w-4 h-4" /> Select an amount
                    </p>
                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                      {suggestedAmounts.map((a) => (
                        <button
                          key={a}
                          type="button"
                          data-cta="donation-amount"
                          onClick={() => setAmount(String(a))}
                          className={`px-4 py-4 rounded-xl border text-sm font-semibold transition-colors ${
                            amount === String(a)
                              ? "bg-primary text-primary-foreground border-primary"
                              : "bg-secondary border-border hover:border-primary/50"
                          }`}
                        >
                          ${a}
                        </button>
                      ))}
                    </div>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-muted-foreground mb-2">Or enter a custom amount</p>
                    <div className="relative max-w-xs">
                      <DollarSign className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                      <Input type="number" min="1" step="1" placeholder="0" value={amount} onChange={(e) => setAmount(e.target.value)} className="pl-8 text-lg" />
                    </div>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-muted-foreground mb-2">Email (optional, for receipt)</p>
                    <Input type="email" placeholder="you@example.com" value={email} onChange={(e) => setEmail(e.target.value)} className="max-w-sm" />
                  </div>
                  <Button size="lg" onClick={handleDonate} disabled={isLoading || !amount} className="w-full sm:w-auto text-lg px-10" data-cta="donation_click" id="donate-primary-checkout">
                    <CreditCard className="w-5 h-5" />
                    {isLoading ? "Processing..." : `Donate${amount ? ` $${amount}` : ""}`}
                  </Button>
                  <p className="text-xs text-muted-foreground">
                    You'll be securely redirected to Stripe to complete your gift. Donations support Klear Path's mission and operating capacity.
                  </p>
                </div>
              </div>
            </div>

            <div className="space-y-6">
              <div className="bg-accent rounded-xl p-6">
                <Shield className="w-8 h-8 text-primary mb-3" />
                <h3 className="font-serif font-semibold text-lg mb-2">Tax-Deductible</h3>
                <p className="text-sm text-muted-foreground mb-3">
                  Klear Path Home, Inc. is a federally recognized 501(c)(3) public charity. Your donation is tax-deductible to the fullest extent permitted by law.
                </p>
                <p className="text-xs text-muted-foreground"><strong>EIN:</strong> 41-3156622</p>
              </div>

              <div className="bg-card rounded-xl p-6 shadow-soft border border-border">
                <Heart className="w-8 h-8 text-primary mb-3" />
                <h3 className="font-serif font-semibold text-lg mb-4">Impact Equations</h3>
                <ul className="space-y-3">
                  {impactTiers.map((t) => (
                    <li key={t.amt} className="flex items-start gap-2 text-sm">
                      <CheckCircle className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                      <span><strong>{t.amt}</strong> — {t.desc}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* DIGNITY BEFORE PAPERWORK */}
      <section className="py-16 lg:py-24 bg-primary text-primary-foreground">
        <div className="container-wide section-padding max-w-3xl">
          <div className="flex items-center gap-3 mb-5">
            <Coffee className="w-8 h-8" />
            <p className="uppercase tracking-wide text-primary-foreground/70 text-sm font-medium">Dignity Before Paperwork</p>
          </div>
          <h2 className="text-3xl lg:text-4xl font-serif font-bold mb-6">Support Starts Before the Forms.</h2>
          <p className="text-lg text-primary-foreground/90 leading-relaxed mb-4">
            Klear Path begins with food, water, safety, trust, and practical support — before overwhelming people with forms, interrogation, or rigid requirements. Temporary aid does not solve permanent problems, and paperwork does not build trust.
          </p>
          <p className="text-lg text-primary-foreground/90 leading-relaxed mb-8">
            Your gift funds the first stabilizing moments that make every next step possible.
          </p>
          <Link to="/dignity-first-model"><Button variant="hero-outline" size="lg">Read the Dignity-First Model<ArrowRight className="w-4 h-4" /></Button></Link>
        </div>
      </section>

      {/* WHERE YOUR DONATION GOES */}
      <section className="py-16 lg:py-24 bg-background">
        <div className="container-wide section-padding">
          <div className="max-w-3xl mb-10">
            <p className="text-primary font-medium mb-3 tracking-wide uppercase text-sm">Where Your Donation Goes</p>
            <h2 className="text-3xl lg:text-4xl font-serif font-bold text-foreground">Every dollar is designed for measurable impact.</h2>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {allocations.map((a) => (
              <div key={a.t} className="bg-card border border-border rounded-xl p-5 flex items-start gap-3">
                <a.icon className="w-5 h-5 text-primary mt-0.5 flex-shrink-0" />
                <p className="font-medium text-foreground text-sm">{a.t}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <EmailCapture />

      <section className="py-16 lg:py-20 bg-secondary">
        <div className="container-wide section-padding">
          <div className="text-center mb-10">
            <h2 className="text-3xl lg:text-4xl font-serif font-semibold text-foreground mb-4">
              Explore More Ways to Move the Mission
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Financial support is one path. Pilot funding, land partnerships, employer relationships, and veteran-focused pathways all move the mission forward.
            </p>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6 max-w-5xl mx-auto">
            <Link to="/fund-a-pilot" className="bg-card rounded-xl p-6 shadow-soft border border-border text-center hover:shadow-medium transition-shadow" data-cta="fund_pilot_click">
              <Handshake className="w-10 h-10 text-primary mx-auto mb-3" />
              <h3 className="font-serif font-semibold text-lg mb-2">Fund a Pilot</h3>
              <p className="text-sm text-muted-foreground">Underwrite pilot deployment and prove a replicable model.</p>
            </Link>
            <Link to="/dignity-first-model" className="bg-card rounded-xl p-6 shadow-soft border border-border text-center hover:shadow-medium transition-shadow">
              <Coffee className="w-10 h-10 text-primary mx-auto mb-3" />
              <h3 className="font-serif font-semibold text-lg mb-2">Dignity-First Model</h3>
              <p className="text-sm text-muted-foreground">See how support begins on Day One — before paperwork.</p>
            </Link>
            <Link to="/veterans" className="bg-card rounded-xl p-6 shadow-soft border border-border text-center hover:shadow-medium transition-shadow" data-cta="veteran_support_click">
              <Heart className="w-10 h-10 text-primary mx-auto mb-3" />
              <h3 className="font-serif font-semibold text-lg mb-2">Support Veterans</h3>
              <p className="text-sm text-muted-foreground">Help build workforce reintegration pathways for veterans.</p>
            </Link>
            <Link to="/housing-stabilization-model" className="bg-card rounded-xl p-6 shadow-soft border border-border text-center hover:shadow-medium transition-shadow">
              <ArrowRight className="w-10 h-10 text-primary mx-auto mb-3" />
              <h3 className="font-serif font-semibold text-lg mb-2">Our Model</h3>
              <p className="text-sm text-muted-foreground">Stabilize. Activate. Retain. The full three-phase framework.</p>
            </Link>
          </div>
        </div>
      </section>
    </Layout>
  );
};

export default Donate;
