import React from 'react';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/Button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import { Users, Globe, Award, Heart, Zap } from 'lucide-react';

export default function About() {
  return (
    <div className="py-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-20">
          <motion.h1 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-4xl md:text-6xl font-bold font-display mb-6"
          >
            Our Mission to <span className="text-primary">Humanize AI</span>
          </motion.h1>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            At ABT IT, we believe that AI should enhance human connection, not replace it. We're building Beraxis as the infrastructure for the next generation of voice communication.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-16 items-center mb-32">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
          >
            <h2 className="text-3xl font-bold font-display mb-6">The Story of Beraxis</h2>
            <p className="text-lg text-muted-foreground mb-6 leading-relaxed">
              Founded in 2023, Beraxis started with a simple observation: business phone calls were stuck in the past. Long wait times, robotic IVRs, and overwhelmed support teams were the norm.
            </p>
            <p className="text-lg text-muted-foreground mb-8 leading-relaxed">
              We set out to create a platform that combines the efficiency of AI with the warmth of human conversation. Today, we help thousands of businesses connect with their customers more effectively than ever before.
            </p>
            <div className="grid grid-cols-2 gap-8">
              <div>
                <h4 className="text-3xl font-bold text-primary font-display">500+</h4>
                <p className="text-sm text-muted-foreground">Companies Trusted</p>
              </div>
              <div>
                <h4 className="text-3xl font-bold text-primary font-display">10M+</h4>
                <p className="text-sm text-muted-foreground">Minutes Processed</p>
              </div>
            </div>
          </motion.div>
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            className="relative"
          >
            <div className="aspect-square rounded-3xl overflow-hidden shadow-2xl border border-white/10">
              <img 
                src="https://picsum.photos/seed/team-work/800/800" 
                alt="Our Team" 
                className="w-full h-full object-cover"
                referrerPolicy="no-referrer"
              />
            </div>
            <div className="absolute -bottom-6 -left-6 bg-primary p-6 rounded-2xl shadow-xl text-black">
              <Award className="w-8 h-8 mb-2" />
              <p className="font-bold">AI Innovation Award 2024</p>
            </div>
          </motion.div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {[
            {
              title: "Customer First",
              desc: "We build for the end-user experience. If the customer is happy, our clients are successful.",
              icon: Heart
            },
            {
              title: "Global Reach",
              desc: "Our team spans 12 countries, bringing diverse perspectives to global communication.",
              icon: Globe
            },
            {
              title: "Innovation Always",
              desc: "We're constantly pushing the boundaries of what's possible with voice AI.",
              icon: Zap
            }
          ].map((value, i) => (
            <Card key={i} className="bg-card/30 backdrop-blur-sm border-border">
              <CardHeader>
                <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
                  <value.icon className="text-primary w-6 h-6" />
                </div>
                <CardTitle>{value.title}</CardTitle>
                <CardDescription className="text-base">{value.desc}</CardDescription>
              </CardHeader>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}
