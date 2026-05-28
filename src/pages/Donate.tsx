import { useState } from "react";
import { Link } from "react-router-dom";
import { Helmet } from "react-helmet-async";
import { Layout } from "@/components/layout/Layout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useToast } from "@/hooks/use-toast";
import { supabase } from "@/integrations/supabase/client";
import { Heart, Shield, CheckCircle, CreditCard, Gift, ArrowRight, DollarSign, Handshake, Repeat } from "lucide-react";
import { EmailCapture } from "@/components/EmailCapture";

const suggestedAmounts = [15, 35, 75, 150, 250, 500];

const Donate = () => {
  const { toast } = useToast();
  const [amount, setAmount] = useState<string>("35");
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
        <title>Donate | Help Build Stability | Klear Path</title>
        <meta name="description" content="Support Klear Path's mission with a secure tax-deductible gift. Your support helps build practical pathways to stability, employment, and independence." />
        <meta name="keywords" content="donate nonprofit, housing stability donation, workforce stability nonprofit, tax deductible charity" />
      </Helmet>

      <section className="py-16 lg:py-24 bg-primary text-primary-foreground" data-page="donate">
        <div className="container-wide section-padding">
          <div className="max-w-4xl">
            <p className="uppercase tracking-wider text-primary-foreground/70 text-xs font-semibold mb-4">
              Secure giving • 501(c)(3) nonprofit • EIN 41-3156622
            </p>
            <h1 className="text-4xl lg:text-6xl font-serif font-bold mb-6">
              Help Someone Move From Crisis To Stability
            </h1>
            <p className="text-xl text-primary-foreground/90 leading-relaxed max-w-3xl">
              Your gift helps Klear Path build practical stabilization pathways through housing support, workforce activation, resource navigation, and long-term accountability.
            </p>
          </div>
        </div>
      </section>

      <section className="py-16 lg:py-24">
        <div className="container-wide section-padding">
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
                  <Button size="lg" onClick={handleDonate} disabled={isLoading || !amount} className="w-full sm:w-auto text-lg px-10" data-cta="donate-primary-checkout">
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
                <h3 className="font-serif font-semibold text-lg mb-4">Monthly Impact</h3>
                <ul className="space-y-3">
                  <li className="flex items-start gap-2 text-sm">
                    <CheckCircle className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                    <span><strong>$15</strong> — Helps support transportation and stabilization needs</span>
                  </li>
                  <li className="flex items-start gap-2 text-sm">
                    <CheckCircle className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                    <span><strong>$35</strong> — Supports readiness planning and resource navigation</span>
                  </li>
                  <li className="flex items-start gap-2 text-sm">
                    <CheckCircle className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                    <span><strong>$75</strong> — Helps fund longer-term stabilization support</span>
                  </li>
                  <li className="flex items-start gap-2 text-sm">
                    <CheckCircle className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                    <span><strong>$150</strong> — Strengthens comprehensive pathway services</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </section>

      <EmailCapture />

      <section className="py-16 lg:py-20 bg-secondary">
        <div className="container-wide section-padding">
          <div className="text-center mb-10">
            <h2 className="text-3xl lg:text-4xl font-serif font-semibold text-foreground mb-4">
              Other Ways to Support
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Financial support is one path. Partnerships, land, expertise, and volunteer energy can also move the mission forward.
            </p>
          </div>
          <div className="grid sm:grid-cols-3 gap-6 max-w-4xl mx-auto">
            <Link to="/partners" className="bg-card rounded-xl p-6 shadow-soft border border-border text-center hover:shadow-medium transition-shadow">
              <Handshake className="w-10 h-10 text-primary mx-auto mb-3" />
              <h3 className="font-serif font-semibold text-lg mb-2">Partner With Us</h3>
              <p className="text-sm text-muted-foreground">Explore collaboration opportunities for foundations, businesses, and organizations.</p>
            </Link>
            <Link to="/housing-stabilization-model" className="bg-card rounded-xl p-6 shadow-soft border border-border text-center hover:shadow-medium transition-shadow">
              <ArrowRight className="w-10 h-10 text-primary mx-auto mb-3" />
              <h3 className="font-serif font-semibold text-lg mb-2">Learn About the Model</h3>
              <p className="text-sm text-muted-foreground">Understand the scalable approach to stabilization and service coordination.</p>
            </Link>
            <Link to="/volunteer" className="bg-card rounded-xl p-6 shadow-soft border border-border text-center hover:shadow-medium transition-shadow">
              <Heart className="w-10 h-10 text-primary mx-auto mb-3" />
              <h3 className="font-serif font-semibold text-lg mb-2">Volunteer</h3>
              <p className="text-sm text-muted-foreground">Give your time and skills to support practical community stabilization work.</p>
            </Link>
          </div>
        </div>
      </section>
    </Layout>
  );
};

export default Donate;
