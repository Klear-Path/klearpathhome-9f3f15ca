import { useState, useEffect } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { Helmet } from "react-helmet-async";
import { Layout } from "@/components/layout/Layout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useToast } from "@/hooks/use-toast";
import { supabase } from "@/integrations/supabase/client";
import { Heart, Shield, CheckCircle, CreditCard, Gift, ArrowRight, DollarSign, Handshake } from "lucide-react";

const suggestedAmounts = [25, 50, 100, 250, 500, 1000];

const Donate = () => {
  const { toast } = useToast();
  const [searchParams] = useSearchParams();
  const [amount, setAmount] = useState<string>("");
  const [email, setEmail] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (searchParams.get("success") === "true") {
      toast({
        title: "Thank you for your donation!",
        description: "Your generous gift helps build pathways from crisis to stability.",
      });
    }
  }, [searchParams, toast]);

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
      if (data?.url) window.open(data.url, "_blank");
    } catch (err: any) {
      toast({ title: "Something went wrong", description: err.message, variant: "destructive" });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Layout>
      <Helmet>
        <title>Donate | Support Housing Stabilization | Klear Path</title>
        <meta name="description" content="Support Klear Path's housing stabilization programs. Your donation helps expand coordinated community support for individuals experiencing homelessness in Bucks and Montgomery Counties." />
        <meta name="keywords" content="donate homelessness, housing stabilization programs, homelessness solutions nonprofit, homelessness prevention initiatives" />
      </Helmet>

      {/* Hero */}
      <section className="py-16 lg:py-24 bg-primary text-primary-foreground">
        <div className="container-wide section-padding">
          <div className="max-w-3xl">
            <h1 className="text-4xl lg:text-5xl font-serif font-bold mb-6">
              Support Housing Stabilization
            </h1>
            <p className="text-xl text-primary-foreground/90 leading-relaxed">
              Your donation helps expand housing stabilization initiatives and coordinated community
              support for individuals experiencing homelessness in Bucks & Montgomery Counties.
              Every dollar strengthens pathways from crisis to stability.
            </p>
          </div>
        </div>
      </section>

      {/* Donation Form */}
      <section className="py-16 lg:py-24">
        <div className="container-wide section-padding">
          <div className="grid lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2">
              <div className="bg-card rounded-2xl shadow-medium border border-border overflow-hidden">
                <div className="bg-primary/5 px-6 py-4 border-b border-border">
                  <h2 className="font-serif text-2xl font-semibold text-foreground">
                    Make Your Donation
                  </h2>
                </div>
                <div className="p-8 lg:p-12 space-y-8">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground mb-3 flex items-center gap-2">
                      <Gift className="w-4 h-4" /> Select an amount
                    </p>
                    <div className="grid grid-cols-3 sm:grid-cols-6 gap-3">
                      {suggestedAmounts.map((a) => (
                        <button
                          key={a}
                          onClick={() => setAmount(String(a))}
                          className={`px-4 py-3 rounded-lg border text-sm font-semibold transition-colors ${
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
                  <Button size="lg" onClick={handleDonate} disabled={isLoading || !amount} className="w-full sm:w-auto text-lg px-10">
                    <CreditCard className="w-5 h-5" />
                    {isLoading ? "Processing..." : `Donate${amount ? ` $${amount}` : ""}`}
                  </Button>
                  <p className="text-xs text-muted-foreground">
                    You'll be securely redirected to Stripe to complete your donation. 100% of your gift goes to our mission.
                  </p>
                </div>
              </div>
            </div>

            {/* Sidebar */}
            <div className="space-y-6">
              <div className="bg-accent rounded-xl p-6">
                <Shield className="w-8 h-8 text-primary mb-3" />
                <h3 className="font-serif font-semibold text-lg mb-2">Tax-Deductible</h3>
                <p className="text-sm text-muted-foreground mb-3">
                  Klear Path Home, Inc. is a federally recognized 501(c)(3) public charity. Your donation is
                  tax-deductible to the fullest extent permitted by law.
                </p>
                <p className="text-xs text-muted-foreground"><strong>EIN:</strong> 41-3156622</p>
              </div>

              <div className="bg-card rounded-xl p-6 shadow-soft border border-border">
                <Heart className="w-8 h-8 text-primary mb-3" />
                <h3 className="font-serif font-semibold text-lg mb-4">Your Impact</h3>
                <ul className="space-y-3">
                  <li className="flex items-start gap-2 text-sm">
                    <CheckCircle className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                    <span><strong>$25</strong> — Provides essential supplies for program participants</span>
                  </li>
                  <li className="flex items-start gap-2 text-sm">
                    <CheckCircle className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                    <span><strong>$100</strong> — Supports job training materials and workforce development</span>
                  </li>
                  <li className="flex items-start gap-2 text-sm">
                    <CheckCircle className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                    <span><strong>$250</strong> — Covers one month of housing stabilization support</span>
                  </li>
                  <li className="flex items-start gap-2 text-sm">
                    <CheckCircle className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                    <span><strong>$1,000</strong> — Sponsors a complete workforce training program</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTAs */}
      <section className="py-16 lg:py-20 bg-secondary">
        <div className="container-wide section-padding">
          <div className="text-center mb-10">
            <h2 className="text-3xl lg:text-4xl font-serif font-semibold text-foreground mb-4">
              Other Ways to Support
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Beyond financial donations, there are many ways to help build community housing partnerships.
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
              <p className="text-sm text-muted-foreground">Understand our scalable approach to housing stabilization and service coordination.</p>
            </Link>
            <Link to="/volunteer" className="bg-card rounded-xl p-6 shadow-soft border border-border text-center hover:shadow-medium transition-shadow">
              <Heart className="w-10 h-10 text-primary mx-auto mb-3" />
              <h3 className="font-serif font-semibold text-lg mb-2">Volunteer</h3>
              <p className="text-sm text-muted-foreground">Give your time and skills to support housing stabilization initiatives.</p>
            </Link>
          </div>
        </div>
      </section>
    </Layout>
  );
};

export default Donate;
