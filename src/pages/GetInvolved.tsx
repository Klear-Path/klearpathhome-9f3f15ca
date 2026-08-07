import { useState } from "react";
import { Link } from "react-router-dom";
import { Layout } from "@/components/layout/Layout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { useToast } from "@/hooks/use-toast";
import { Users, Building2, Heart, Briefcase, Clock, Hammer, Utensils, BookOpen, CheckCircle } from "lucide-react";
import { HoneypotField } from "@/components/HoneypotField";
import { submitContactSubmission, submissionErrorMessage } from "@/lib/forms";

const emptyForm = {
  name: "",
  email: "",
  phone: "",
  type: "volunteer",
  interests: [] as string[],
  message: ""
};

const GetInvolved = () => {
  const { toast } = useToast();
  const [formData, setFormData] = useState(emptyForm);
  const [honeypot, setHoneypot] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      await submitContactSubmission({
        form: "get-involved",
        name: formData.name,
        email: formData.email,
        phone: formData.phone,
        inquiryType: formData.type,
        interests: formData.interests,
        message: formData.message,
        honeypot,
      });

      toast({
        title: "Thank you for your interest!",
        description: "We'll be in touch soon to discuss how you can get involved.",
      });
      setFormData(emptyForm);
    } catch (error) {
      toast({
        variant: "destructive",
        title: "That didn't send",
        description: submissionErrorMessage(error),
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const toggleInterest = (interest: string) => {
    setFormData(prev => ({
      ...prev,
      interests: prev.interests.includes(interest)
        ? prev.interests.filter(i => i !== interest)
        : [...prev.interests, interest]
    }));
  };

  const volunteerOpportunities = [
    { icon: Hammer, title: "Construction & Setup", description: "Help build and maintain campus facilities" },
    { icon: Utensils, title: "Meal Service", description: "Prepare and serve meals at the Safety Center" },
    { icon: BookOpen, title: "Skills Training", description: "Share professional skills with residents" },
    { icon: Users, title: "Mentorship", description: "Provide guidance and support to program participants" },
  ];

  return (
    <Layout>
      {/* Hero */}
      <section className="py-16 lg:py-24 bg-primary text-primary-foreground">
        <div className="container-wide section-padding">
          <div className="max-w-3xl">
            <h1 className="text-4xl lg:text-5xl font-serif font-bold mb-6">
              Get Involved
            </h1>
            <p className="text-xl text-primary-foreground/90 leading-relaxed">
              Whether you want to volunteer your time, partner as an organization, or support 
              our mission in other ways—there's a place for you at Klear Path.
            </p>
          </div>
        </div>
      </section>

      {/* Ways to Help */}
      <section className="py-16 lg:py-24">
        <div className="container-wide section-padding">
          <div className="text-center mb-12">
            <h2 className="text-3xl lg:text-4xl font-serif font-semibold text-foreground mb-4">
              Ways to Make a Difference
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Every contribution—time, expertise, or resources—helps build pathways to stability.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6 mb-16">
            <div className="bg-card rounded-xl p-6 shadow-soft border border-border text-center">
              <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mx-auto mb-4">
                <Users className="w-8 h-8 text-primary" />
              </div>
              <h3 className="font-serif font-semibold text-xl mb-3">Volunteer</h3>
              <p className="text-muted-foreground mb-4">
                Give your time and skills to support our programs and residents.
              </p>
            </div>
            
            <div className="bg-card rounded-xl p-6 shadow-soft border border-border text-center">
              <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mx-auto mb-4">
                <Building2 className="w-8 h-8 text-primary" />
              </div>
              <h3 className="font-serif font-semibold text-xl mb-3">Partner</h3>
              <p className="text-muted-foreground mb-4">
                Organizations can collaborate through sponsorships, in-kind donations, or 
                employee volunteer programs.
              </p>
            </div>
            
            <div className="bg-card rounded-xl p-6 shadow-soft border border-border text-center">
              <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mx-auto mb-4">
                <Heart className="w-8 h-8 text-primary" />
              </div>
              <h3 className="font-serif font-semibold text-xl mb-3">Donate</h3>
              <p className="text-muted-foreground mb-4">
                Financial support at any level helps us serve more neighbors in need.
              </p>
              <Link to="/donate">
                <Button variant="outline" size="sm">Go to Donate Page</Button>
              </Link>
            </div>
          </div>

          {/* Volunteer Opportunities */}
          <div className="bg-secondary rounded-2xl p-8 lg:p-10">
            <h3 className="font-serif text-2xl font-semibold text-center mb-8">
              Volunteer Opportunities
            </h3>
            <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
              {volunteerOpportunities.map((opp) => (
                <div key={opp.title} className="bg-card rounded-xl p-5 text-center shadow-soft">
                  <opp.icon className="w-8 h-8 text-primary mx-auto mb-3" />
                  <h4 className="font-semibold mb-2">{opp.title}</h4>
                  <p className="text-sm text-muted-foreground">{opp.description}</p>
                </div>
              ))}
            </div>
            <div className="text-center mt-8">
              <div className="flex items-center justify-center gap-2 text-muted-foreground">
                <Clock className="w-4 h-4" />
                <span className="text-sm">Flexible scheduling available—weekdays, evenings, and weekends</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Interest Form */}
      <section className="py-16 lg:py-24 bg-accent">
        <div className="container-wide section-padding">
          <div className="max-w-2xl mx-auto">
            <div className="text-center mb-10">
              <h2 className="text-3xl lg:text-4xl font-serif font-semibold text-foreground mb-4">
                Express Your Interest
              </h2>
              <p className="text-lg text-muted-foreground">
                Tell us how you'd like to get involved, and we'll connect you with the right opportunity.
              </p>
            </div>

            <form onSubmit={handleSubmit} className="relative bg-card rounded-2xl p-8 shadow-medium border border-border">
              <HoneypotField id="get-involved-website" value={honeypot} onChange={setHoneypot} />
              <div className="space-y-6">
                <div className="grid sm:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="name">Full Name *</Label>
                    <Input
                      id="name"
                      required
                      value={formData.name}
                      onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                      placeholder="Your name"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="email">Email *</Label>
                    <Input
                      id="email"
                      type="email"
                      required
                      value={formData.email}
                      onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
                      placeholder="you@example.com"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="phone">Phone Number</Label>
                  <Input
                    id="phone"
                    type="tel"
                    value={formData.phone}
                    onChange={(e) => setFormData(prev => ({ ...prev, phone: e.target.value }))}
                    placeholder="(215) 555-1234"
                  />
                </div>

                <div className="space-y-3">
                  <Label>I'm interested in: *</Label>
                  <div className="flex flex-wrap gap-2">
                    {[
                      { value: "volunteer", label: "Volunteering" },
                      { value: "corporate", label: "Corporate Partnership" },
                      { value: "faith", label: "Faith Community Partnership" },
                      { value: "inkind", label: "In-Kind Donation" },
                      { value: "other", label: "Other" },
                    ].map((option) => (
                      <button
                        key={option.value}
                        type="button"
                        onClick={() => toggleInterest(option.value)}
                        className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
                          formData.interests.includes(option.value)
                            ? "bg-primary text-primary-foreground"
                            : "bg-secondary text-secondary-foreground hover:bg-secondary/80"
                        }`}
                      >
                        {formData.interests.includes(option.value) && (
                          <CheckCircle className="w-4 h-4 inline mr-1" />
                        )}
                        {option.label}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="message">Tell us more (optional)</Label>
                  <Textarea
                    id="message"
                    value={formData.message}
                    onChange={(e) => setFormData(prev => ({ ...prev, message: e.target.value }))}
                    placeholder="Share any skills, availability, or questions..."
                    rows={4}
                  />
                </div>

                <Button type="submit" size="lg" className="w-full" disabled={isSubmitting || formData.interests.length === 0}>
                  {isSubmitting ? "Submitting..." : "Submit Interest Form"}
                </Button>
              </div>
            </form>
          </div>
        </div>
      </section>

      {/* Corporate Partners */}
      <section className="py-16 lg:py-24">
        <div className="container-wide section-padding">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl lg:text-4xl font-serif font-semibold text-foreground mb-4">
                Corporate & Organizational Partners
              </h2>
              <p className="text-lg text-muted-foreground leading-relaxed mb-6">
                Businesses and organizations can make a significant impact through structured 
                partnerships that benefit both your team and our community.
              </p>
              <ul className="space-y-3">
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-primary mt-0.5 flex-shrink-0" />
                  <span><strong>Sponsorship Packages</strong> — Support specific programs or capital needs</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-primary mt-0.5 flex-shrink-0" />
                  <span><strong>Employee Volunteer Days</strong> — Team-building with purpose</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-primary mt-0.5 flex-shrink-0" />
                  <span><strong>In-Kind Donations</strong> — Materials, supplies, and professional services</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-primary mt-0.5 flex-shrink-0" />
                  <span><strong>Matching Gift Programs</strong> — Double your employees' impact</span>
                </li>
              </ul>
            </div>
            <div className="bg-primary rounded-2xl p-8 text-primary-foreground">
              <Briefcase className="w-12 h-12 mb-4" />
              <h3 className="font-serif text-2xl font-semibold mb-4">
                Workforce Development Partners
              </h3>
              <p className="text-primary-foreground/90 mb-6">
                We're seeking employers willing to hire program graduates. If your company 
                needs skilled workers in construction, solar installation, or related fields—we 
                can provide trained, motivated candidates.
              </p>
              <Link to="/contact">
                <Button variant="hero">Contact Us About Hiring</Button>
              </Link>
            </div>
          </div>
        </div>
      </section>
    </Layout>
  );
};

export default GetInvolved;
