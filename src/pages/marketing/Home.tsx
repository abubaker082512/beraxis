import React from 'react';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/Button';
import { Link } from 'react-router-dom';
import { 
  Phone, 
  Cpu, 
  Zap, 
  Shield, 
  ArrowRight, 
  CheckCircle2, 
  Play,
  MessageSquare,
  Globe,
  Users,
  BarChart3
} from 'lucide-react';

export default function Home() {
  return (
    <div className="overflow-hidden">
      {/* Hero Section */}
      <section className="relative pt-20 pb-32 md:pt-32 md:pb-48">
        {/* Background Glows */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-6xl h-[600px] bg-primary/10 blur-[120px] -z-10 rounded-full"></div>
        <div className="absolute top-40 left-0 w-64 h-64 bg-primary/5 blur-[80px] -z-10 rounded-full"></div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-primary/10 border border-primary/20 text-primary text-sm font-medium mb-8">
              <Zap className="w-4 h-4" />
              <span>v2.0 is now live with Voice Cloning</span>
            </div>
            <h1 className="text-5xl md:text-7xl font-bold font-display tracking-tight mb-6 leading-[1.1]">
              Human-Like <span className="text-primary">AI Voice Agents</span> <br />
              That Scale Your Business
            </h1>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto mb-10 leading-relaxed">
              Automate your outbound sales and inbound support with AI agents that sound human, never sleep, and integrate with your existing tools.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-6">
              <Link to="/register">
                <Button size="lg" className="w-full sm:w-auto text-lg px-10">
                  Start Calling Now
                  <ArrowRight className="ml-2 w-5 h-5" />
                </Button>
              </Link>
              <Link to="/book-demo">
                <Button variant="outline" size="lg" className="w-full sm:w-auto text-lg px-10">
                  <Play className="mr-2 w-5 h-5 fill-current" />
                  Watch Demo
                </Button>
              </Link>
            </div>
          </motion.div>

          {/* AI Voice Animation Placeholder */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.3, duration: 0.8 }}
            className="mt-20 relative max-w-4xl mx-auto"
          >
            <div className="aspect-video rounded-2xl border border-white/10 glass p-4 shadow-2xl overflow-hidden group">
              <div className="absolute inset-0 bg-gradient-to-t from-background via-transparent to-transparent z-10"></div>
              <div className="relative z-20 h-full flex flex-col items-center justify-center">
                {/* Simulated Voice Waves */}
                <div className="flex items-center space-x-1 h-32">
                  {[...Array(20)].map((_, i) => (
                    <motion.div
                      key={i}
                      animate={{ 
                        height: [20, Math.random() * 80 + 20, 20],
                      }}
                      transition={{ 
                        repeat: Infinity, 
                        duration: 1 + Math.random(),
                        ease: "easeInOut"
                      }}
                      className="w-1.5 bg-primary rounded-full neon-glow"
                    />
                  ))}
                </div>
                <div className="mt-8 text-primary font-display font-medium tracking-widest uppercase text-sm">
                  AI Agent Speaking...
                </div>
              </div>
              <img 
                src="https://picsum.photos/seed/ai-tech/1200/800" 
                alt="Dashboard Preview" 
                className="absolute inset-0 w-full h-full object-cover opacity-20 group-hover:scale-105 transition-transform duration-1000"
                referrerPolicy="no-referrer"
              />
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="py-24 bg-card/50 relative">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-bold font-display mb-4">Everything you need to scale</h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              Our platform combines state-of-the-art LLMs with ultra-low latency TTS for a seamless experience.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              {
                title: "Ultra-Low Latency",
                desc: "Sub-500ms response times for natural, fluid conversations that never feel robotic.",
                icon: Zap
              },
              {
                title: "Human-Like Voices",
                desc: "Choose from 100+ premium voices or clone your own for a consistent brand identity.",
                icon: MessageSquare
              },
              {
                title: "Smart Integration",
                desc: "Connect with Twilio, SIP providers, and your CRM with just a few clicks.",
                icon: Globe
              },
              {
                title: "Campaign Management",
                desc: "Run thousands of calls simultaneously with automated lead management.",
                icon: Users
              },
              {
                title: "Real-time Analytics",
                desc: "Track sentiment, conversion rates, and call duration in our advanced dashboard.",
                icon: BarChart3
              },
              {
                title: "Enterprise Security",
                desc: "SOC2 compliant, end-to-end encryption, and multi-tenant architecture.",
                icon: Shield
              }
            ].map((feature, i) => (
              <motion.div
                key={i}
                whileHover={{ y: -5 }}
                className="p-8 rounded-2xl border border-border bg-background hover:border-primary/50 transition-all group"
              >
                <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-6 group-hover:bg-primary group-hover:text-black transition-colors">
                  <feature.icon className="w-6 h-6" />
                </div>
                <h3 className="text-xl font-bold mb-3 font-display">{feature.title}</h3>
                <p className="text-muted-foreground leading-relaxed">{feature.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Social Proof / Trusted By */}
      <section className="py-20 border-y border-border">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <p className="text-sm font-medium text-muted-foreground uppercase tracking-widest mb-10">Trusted by 500+ forward-thinking companies</p>
          <div className="flex flex-wrap justify-center items-center gap-12 opacity-50 grayscale hover:grayscale-0 transition-all">
            {/* Logo Placeholders */}
            <div className="text-2xl font-bold font-display">TECHCORP</div>
            <div className="text-2xl font-bold font-display">NEXUS AI</div>
            <div className="text-2xl font-bold font-display">VOX MEDIA</div>
            <div className="text-2xl font-bold font-display">GLOBAL SALES</div>
            <div className="text-2xl font-bold font-display">CLOUD SYSTEMS</div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 relative overflow-hidden">
        <div className="absolute inset-0 bg-primary/5 -z-10"></div>
        <div className="max-w-5xl mx-auto px-4 text-center">
          <h2 className="text-4xl md:text-6xl font-bold font-display mb-8">Ready to automate your <span className="text-primary">voice operations?</span></h2>
          <p className="text-xl text-muted-foreground mb-12 max-w-2xl mx-auto">
            Join hundreds of businesses using Beraxis to increase their reach and reduce operational costs.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-6">
            <Link to="/register">
              <Button size="lg" className="px-12 py-6 text-xl">Get Started Free</Button>
            </Link>
            <Link to="/pricing">
              <Button variant="outline" size="lg" className="px-12 py-6 text-xl">View Pricing</Button>
            </Link>
          </div>
          <div className="mt-12 flex items-center justify-center space-x-8 text-sm text-muted-foreground">
            <div className="flex items-center space-x-2">
              <CheckCircle2 className="text-primary w-4 h-4" />
              <span>No credit card required</span>
            </div>
            <div className="flex items-center space-x-2">
              <CheckCircle2 className="text-primary w-4 h-4" />
              <span>14-day free trial</span>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
