import { Link } from "react-router-dom";
import { Layout } from "@/components/layout/Layout";
import { Button } from "@/components/ui/button";
import { Heart, Shield, CheckCircle, CreditCard, Calendar, Gift, Building2, ArrowRight } from "lucide-react";

const Donate = () => {
  const oneTimeAmounts = [25, 50, 100, 250, 500, 1000];
  const monthlyAmounts = [10, 25, 50, 100, 250];

  return (
    <Layout>
      {/* Hero */}
      <section className="py-16 lg:py-24 bg-primary text-primary-foreground">
        <div className="container-wide section-padding">
          <div className="max-w-3xl">
            <h1 className="text-4xl lg:text-5xl font-serif font-bold mb-6">
              Support Our Mission
            </h1>
            <p className="text-xl text-primary-foreground/90 leading-relaxed">
              Your donation helps build pathways from crisis to stability for our neighbors in
              Bucks and Montgomery Counties. Every dollar makes a difference.
            </p>
          </div>
        </div>
      </section>

      {/* Donation Section */}
      <section className="py-16 lg:py-24">
        <div className="container-wide section-padding">
          <div className="grid lg:grid-cols-3 gap-8">
            {/* Zeffy Embed Placeholder */}
            <div className="lg:col-span-2">
              <div className="bg-card rounded-2xl shadow-medium border border-border overflow-hidden">
                <div className="bg-primary/5 px-6 py-4 border-b border-border">
                  <h2 className="font-serif text-2xl font-semibold text-foreground">
                    Make Your Donation
                  </h2>
                </div>
                
                {/* Zeffy Embed Placeholder */}
                <div className="p-8 lg:p-12">
                  <div className="bg-secondary rounded-xl p-8 text-center border-2 border-dashed border-border min-h-[400px] flex flex-col items-center justify-center">
                    <CreditCard className="w-16 h-16 text-muted-foreground mb-4" />
                    <h3 className="font-serif text-xl font-semibold mb-2">Zeffy Donation Form</h3>
                    <p className="text-muted-foreground mb-6 max-w-md">
                      Secure donation processing will be embedded here. Zeffy charges no fees
                      on donations—100% of your gift goes to our mission.
                    </p>
                    <div className="bg-accent rounded-lg p-4 text-sm text-muted-foreground">
                      <p className="font-medium text-foreground mb-1">Embed Code Placeholder</p>
                      <code className="text-xs">&lt;iframe src="zeffy-form-url"&gt;&lt;/iframe&gt;</code>
                    </div>
                  </div>
                </div>

                {/* Suggested Amounts Reference */}
                <div className="px-8 pb-8">
                  <div className="grid sm:grid-cols-2 gap-6">
                    <div>
                      <h4 className="font-semibold text-sm text-muted-foreground mb-3 flex items-center gap-2">
                        <Gift className="w-4 h-4" /> Suggested One-Time Gifts
                      </h4>
                      <div className="flex flex-wrap gap-2">
                        {oneTimeAmounts.map((amount) => (
                          <span key={amount} className="px-3 py-1 bg-secondary rounded-full text-sm font-medium">
                            ${amount}
                          </span>
                        ))}
                      </div>
                    </div>
                    <div>
                      <h4 className="font-semibold text-sm text-muted-foreground mb-3 flex items-center gap-2">
                        <Calendar className="w-4 h-4" /> Suggested Monthly Gifts
                      </h4>
                      <div className="flex flex-wrap gap-2">
                        {monthlyAmounts.map((amount) => (
                          <span key={amount} className="px-3 py-1 bg-secondary rounded-full text-sm font-medium">
                            ${amount}/mo
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Sidebar */}
            <div className="space-y-6">
              {/* Tax Info */}
              <div className="bg-accent rounded-xl p-6">
                <Shield className="w-8 h-8 text-primary mb-3" />
                <h3 className="font-serif font-semibold text-lg mb-2">Tax-Deductible</h3>
                <p className="text-sm text-muted-foreground mb-3">
                  Klear Path Home, Inc. is a federally recognized 501(c)(3) public charity. Your donation is
                  tax-deductible to the extent allowed by law.
                </p>
                <p className="text-xs text-muted-foreground">
                  <strong>EIN:</strong> 41-3156622
                </p>
              </div>

              {/* Impact */}
              <div className="bg-card rounded-xl p-6 shadow-soft border border-border">
                <Heart className="w-8 h-8 text-primary mb-3" />
                <h3 className="font-serif font-semibold text-lg mb-4">Your Impact</h3>
                <ul className="space-y-3">
                  <li className="flex items-start gap-2 text-sm">
                    <CheckCircle className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                    <span><strong>$25</strong> — Provides a week of hot meals at the Safety Center</span>
                  </li>
                  <li className="flex items-start gap-2 text-sm">
                    <CheckCircle className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                    <span><strong>$100</strong> — Supplies job training materials for one resident</span>
                  </li>
                  <li className="flex items-start gap-2 text-sm">
                    <CheckCircle className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                    <span><strong>$250</strong> — Covers one month of housing support services</span>
                  </li>
                  <li className="flex items-start gap-2 text-sm">
                    <CheckCircle className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                    <span><strong>$1,000</strong> — Sponsors a complete workforce training program</span>
                  </li>
                </ul>
              </div>

              {/* Monthly Giving */}
              <div className="bg-primary rounded-xl p-6 text-primary-foreground">
                <Calendar className="w-8 h-8 mb-3" />
                <h3 className="font-serif font-semibold text-lg mb-2">Become a Monthly Giver</h3>
                <p className="text-sm text-primary-foreground/90">
                  Monthly donors provide sustainable support that helps us plan and grow. Join
                  our community of regular givers.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Other Ways to Give */}
      <section className="py-16 lg:py-24 bg-secondary">
        <div className="container-wide section-padding">
          <div className="text-center mb-12">
            <h2 className="text-3xl lg:text-4xl font-serif font-semibold text-foreground mb-4">
              Other Ways to Give
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Beyond online donations, there are many ways to support our mission.
            </p>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-card rounded-xl p-6 shadow-soft border border-border">
              <h3 className="font-serif font-semibold mb-2">Mail a Check</h3>
              <p className="text-sm text-muted-foreground mb-3">
                Make checks payable to "Klear Path Home, Inc." and mail to our office.
              </p>
              <Link to="/contact" className="text-primary text-sm font-medium hover:underline">
                Get mailing address →
              </Link>
            </div>
            
            <div className="bg-card rounded-xl p-6 shadow-soft border border-border">
              <h3 className="font-serif font-semibold mb-2">Donor-Advised Fund</h3>
              <p className="text-sm text-muted-foreground mb-3">
                Recommend a grant from your DAF to Klear Path Home, Inc. (EIN: 41-3156622).
              </p>
            </div>
            
            <div className="bg-card rounded-xl p-6 shadow-soft border border-border">
              <h3 className="font-serif font-semibold mb-2">Stock Donation</h3>
              <p className="text-sm text-muted-foreground mb-3">
                Donate appreciated securities for potential tax benefits.
              </p>
              <Link to="/contact" className="text-primary text-sm font-medium hover:underline">
                Contact us for details →
              </Link>
            </div>
            
            <div className="bg-card rounded-xl p-6 shadow-soft border border-border">
              <h3 className="font-serif font-semibold mb-2">Planned Giving</h3>
              <p className="text-sm text-muted-foreground mb-3">
                Include Klear Path in your estate planning to leave a lasting legacy.
              </p>
              <Link to="/contact" className="text-primary text-sm font-medium hover:underline">
                Learn more →
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Corporate Giving */}
      <section className="py-16 lg:py-20">
        <div className="container-wide section-padding">
          <div className="bg-card rounded-2xl p-8 lg:p-12 shadow-medium border border-border grid lg:grid-cols-2 gap-8 items-center">
            <div>
              <Building2 className="w-12 h-12 text-primary mb-4" />
              <h2 className="text-3xl font-serif font-semibold text-foreground mb-4">
                Corporate & Foundation Giving
              </h2>
              <p className="text-muted-foreground mb-6">
                Businesses and foundations can make transformative gifts through grants,
                matching programs, and sponsorships. We offer naming opportunities and
                recognition for major donors.
              </p>
              <Link to="/contact">
                <Button size="lg">
                  Discuss a Partnership
                  <ArrowRight className="w-4 h-4" />
                </Button>
              </Link>
            </div>
            <div className="bg-accent rounded-xl p-6">
              <h3 className="font-serif font-semibold text-lg mb-4">Partnership Benefits</h3>
              <ul className="space-y-2">
                <li className="flex items-start gap-2 text-sm">
                  <CheckCircle className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                  <span>Recognition in annual reports and materials</span>
                </li>
                <li className="flex items-start gap-2 text-sm">
                  <CheckCircle className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                  <span>Naming opportunities for major gifts</span>
                </li>
                <li className="flex items-start gap-2 text-sm">
                  <CheckCircle className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                  <span>Employee engagement opportunities</span>
                </li>
                <li className="flex items-start gap-2 text-sm">
                  <CheckCircle className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                  <span>Customized impact reporting</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>
    </Layout>
  );
};

export default Donate;
