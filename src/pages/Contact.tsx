import { useState } from "react";
import { Layout } from "@/components/layout/Layout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { useToast } from "@/hooks/use-toast";
import { Mail, Phone, MapPin, Clock, Send } from "lucide-react";

const Contact = () => {
  const { toast } = useToast();
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    phone: "",
    subject: "",
    message: ""
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    // Simulate form submission
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    toast({
      title: "Message sent!",
      description: "Thank you for reaching out. We'll respond within 2 business days.",
    });
    
    setFormData({
      name: "",
      email: "",
      phone: "",
      subject: "",
      message: ""
    });
    setIsSubmitting(false);
  };

  return (
    <Layout>
      {/* Hero */}
      <section className="py-16 lg:py-24 bg-primary text-primary-foreground">
        <div className="container-wide section-padding">
          <div className="max-w-3xl">
            <h1 className="text-4xl lg:text-5xl font-serif font-bold mb-6">
              Contact Us
            </h1>
            <p className="text-xl text-primary-foreground/90 leading-relaxed">
              Have questions about our programs, interested in partnership, or want to get 
              involved? We'd love to hear from you.
            </p>
          </div>
        </div>
      </section>

      {/* Contact Section */}
      <section className="py-16 lg:py-24">
        <div className="container-wide section-padding">
          <div className="grid lg:grid-cols-3 gap-8">
            {/* Contact Form */}
            <div className="lg:col-span-2">
              <div className="bg-card rounded-2xl p-8 shadow-medium border border-border">
                <h2 className="font-serif text-2xl font-semibold mb-6">Send Us a Message</h2>
                
                <form onSubmit={handleSubmit} className="space-y-6">
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

                  <div className="grid sm:grid-cols-2 gap-4">
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
                    <div className="space-y-2">
                      <Label htmlFor="subject">Subject *</Label>
                      <Input
                        id="subject"
                        required
                        value={formData.subject}
                        onChange={(e) => setFormData(prev => ({ ...prev, subject: e.target.value }))}
                        placeholder="What is this regarding?"
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="message">Message *</Label>
                    <Textarea
                      id="message"
                      required
                      value={formData.message}
                      onChange={(e) => setFormData(prev => ({ ...prev, message: e.target.value }))}
                      placeholder="How can we help you?"
                      rows={6}
                    />
                  </div>

                  <Button type="submit" size="lg" disabled={isSubmitting}>
                    {isSubmitting ? (
                      "Sending..."
                    ) : (
                      <>
                        <Send className="w-4 h-4" />
                        Send Message
                      </>
                    )}
                  </Button>
                </form>
              </div>
            </div>

            {/* Contact Info Sidebar */}
            <div className="space-y-6">
              <div className="bg-accent rounded-xl p-6">
                <Mail className="w-8 h-8 text-primary mb-3" />
                <h3 className="font-serif font-semibold text-lg mb-2">Email</h3>
                <a 
                  href="mailto:info@klearpathhome.org" 
                  className="text-primary hover:underline"
                >
                  info@klearpathhome.org
                </a>
                <p className="text-sm text-muted-foreground mt-2">
                  For general inquiries and information
                </p>
              </div>

              <div className="bg-accent rounded-xl p-6">
                <Phone className="w-8 h-8 text-primary mb-3" />
                <h3 className="font-serif font-semibold text-lg mb-2">Phone</h3>
                <a 
                  href="tel:+12155551234" 
                  className="text-primary hover:underline"
                >
                  (215) 555-1234
                </a>
                <p className="text-sm text-muted-foreground mt-2">
                  Monday - Friday, 9am - 5pm EST
                </p>
              </div>

              <div className="bg-accent rounded-xl p-6">
                <MapPin className="w-8 h-8 text-primary mb-3" />
                <h3 className="font-serif font-semibold text-lg mb-2">Service Area</h3>
                <p className="text-foreground">
                  Bucks & Montgomery Counties<br />
                  Pennsylvania
                </p>
                <p className="text-sm text-muted-foreground mt-2">
                  Campus location to be announced
                </p>
              </div>

              <div className="bg-primary rounded-xl p-6 text-primary-foreground">
                <Clock className="w-8 h-8 mb-3" />
                <h3 className="font-serif font-semibold text-lg mb-2">Response Time</h3>
                <p className="text-primary-foreground/90 text-sm">
                  We aim to respond to all inquiries within 2 business days. For urgent 
                  partnership or media inquiries, please indicate that in your subject line.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* FAQ Preview */}
      <section className="py-16 lg:py-24 bg-secondary">
        <div className="container-wide section-padding">
          <div className="max-w-3xl mx-auto text-center">
            <h2 className="text-3xl lg:text-4xl font-serif font-semibold text-foreground mb-4">
              Common Questions
            </h2>
            <p className="text-lg text-muted-foreground mb-8">
              Here are answers to some frequently asked questions.
            </p>

            <div className="text-left space-y-6">
              <div className="bg-card rounded-xl p-6 shadow-soft border border-border">
                <h3 className="font-semibold mb-2">Is Klear Path operational yet?</h3>
                <p className="text-muted-foreground text-sm">
                  We are currently in the development phase, seeking a land partner to build 
                  our first campus. Once we secure a site, construction will begin on the 
                  Safety Center and micro-village housing.
                </p>
              </div>

              <div className="bg-card rounded-xl p-6 shadow-soft border border-border">
                <h3 className="font-semibold mb-2">How can I refer someone who needs help?</h3>
                <p className="text-muted-foreground text-sm">
                  While our campus is under development, we're happy to connect individuals 
                  with existing resources in Bucks and Montgomery Counties. Please contact us 
                  and we'll do our best to help.
                </p>
              </div>

              <div className="bg-card rounded-xl p-6 shadow-soft border border-border">
                <h3 className="font-semibold mb-2">Are donations tax-deductible?</h3>
                <p className="text-muted-foreground text-sm">
                  Yes. Klear Path Home, Inc. is a federally recognized 501(c)(3) public charity 
                  (EIN: 41-3156622). Your donation is tax-deductible to the extent allowed by law.
                </p>
              </div>

              <div className="bg-card rounded-xl p-6 shadow-soft border border-border">
                <h3 className="font-semibold mb-2">Can I request financial documents?</h3>
                <p className="text-muted-foreground text-sm">
                  Absolutely. Our IRS Form 990 and other governance documents are available 
                  upon request. Transparency is a core value of our organization.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>
    </Layout>
  );
};

export default Contact;
