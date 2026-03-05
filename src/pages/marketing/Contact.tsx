import React from 'react';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Card, CardContent } from '@/components/ui/Card';
import { Mail, Phone, MapPin, Send } from 'lucide-react';

export default function Contact() {
  return (
    <div className="py-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <motion.h1 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-4xl md:text-6xl font-bold font-display mb-6"
          >
            Get in <span className="text-primary">Touch</span>
          </motion.h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Have questions about our AI calling platform? We're here to help.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
          {/* Contact Info */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
          >
            <div className="space-y-8">
              <div className="flex items-start space-x-6">
                <div className="p-4 bg-primary/10 rounded-2xl">
                  <Mail className="text-primary w-6 h-6" />
                </div>
                <div>
                  <h4 className="text-xl font-bold font-display mb-1">Email Us</h4>
                  <p className="text-muted-foreground">support@abtaicaller.com</p>
                  <p className="text-muted-foreground">sales@abtaicaller.com</p>
                </div>
              </div>
              <div className="flex items-start space-x-6">
                <div className="p-4 bg-primary/10 rounded-2xl">
                  <Phone className="text-primary w-6 h-6" />
                </div>
                <div>
                  <h4 className="text-xl font-bold font-display mb-1">Call Us</h4>
                  <p className="text-muted-foreground">+1 (555) 123-4567</p>
                  <p className="text-muted-foreground">Mon-Fri, 9am-6pm EST</p>
                </div>
              </div>
              <div className="flex items-start space-x-6">
                <div className="p-4 bg-primary/10 rounded-2xl">
                  <MapPin className="text-primary w-6 h-6" />
                </div>
                <div>
                  <h4 className="text-xl font-bold font-display mb-1">Visit Us</h4>
                  <p className="text-muted-foreground">123 AI Boulevard, Suite 500</p>
                  <p className="text-muted-foreground">Tech City, CA 94103</p>
                </div>
              </div>
            </div>

            <div className="mt-12 p-8 rounded-3xl bg-card border border-border relative overflow-hidden">
              <div className="absolute top-0 right-0 w-32 h-32 bg-primary/5 blur-3xl rounded-full"></div>
              <h3 className="text-2xl font-bold font-display mb-4">Enterprise Inquiries</h3>
              <p className="text-muted-foreground mb-6">
                Looking for a custom solution or high-volume pricing? Our enterprise team is ready to assist.
              </p>
              <Button variant="outline">Schedule a Call</Button>
            </div>
          </motion.div>

          {/* Contact Form */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
          >
            <Card className="p-8 border-border bg-card/50 backdrop-blur-sm">
              <form className="space-y-6">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <label className="text-sm font-medium">First Name</label>
                    <Input placeholder="John" />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Last Name</label>
                    <Input placeholder="Doe" />
                  </div>
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Work Email</label>
                  <Input type="email" placeholder="john@company.com" />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Company</label>
                  <Input placeholder="Acme Inc." />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Message</label>
                  <textarea 
                    className="flex min-h-[120px] w-full rounded-md border border-border bg-background px-3 py-2 text-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary transition-all"
                    placeholder="Tell us about your needs..."
                  ></textarea>
                </div>
                <Button className="w-full py-6 text-lg">
                  Send Message
                  <Send className="ml-2 w-5 h-5" />
                </Button>
              </form>
            </Card>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
