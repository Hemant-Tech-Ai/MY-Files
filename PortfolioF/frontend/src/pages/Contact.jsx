import React, { useState } from 'react';
import { FaEnvelope, FaPhone, FaMapMarkerAlt, FaTwitter, FaReddit, FaLinkedinIn, FaGithub } from 'react-icons/fa';
import { SiOpenai } from 'react-icons/si';
import { contactAPI } from '../services/api';
import '../styles/pages/contact.css';

const Contact = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    message: ''
  });
  const [formStatus, setFormStatus] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prevData => ({
      ...prevData,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    try {
      // Use the contactAPI service
      await contactAPI.sendMessage(formData);
      
      // Reset form
      setFormData({
        name: '',
        email: '',
        subject: '',
        message: ''
      });
      
      setFormStatus({
        type: 'success',
        message: 'Your message has been sent successfully!'
      });
      
      // Clear success message after 5 seconds
      setTimeout(() => {
        setFormStatus(null);
      }, 5000);
      
    } catch (error) {
      console.error('Error sending message:', error);
      setFormStatus({
        type: 'error',
        message: 'Failed to send message. Please try again.'
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <section className="contact">
      <div className="container">
        <div className="contact-intro">
          <h1 className="section-title">Get In Touch</h1>
          <p>Feel free to reach out to me for any questions or opportunities!</p>
        </div>
        
        <div className="contact-card">
          <div className="contact-info">
            <div className="contact-header">
              <h2>Hemant Singh Sidar</h2>
              <p className="contact-subtitle">Let's connect and discuss how we can work together</p>
            </div>
            
            <div className="contact-details">
              <div className="info-item">
                <div className="info-icon">
                  <FaEnvelope />
                </div>
                <div className="info-content">
                  <h3>Email</h3>
                  <p><a href="mailto:contact@hemantsinghsidar.com">contact@hemantsinghsidar.com</a></p>
                </div>
              </div>
              
              <div className="info-item">
                <div className="info-icon">
                  <FaPhone />
                </div>
                <div className="info-content">
                  <h3>Phone</h3>
                  <p><a href="tel:+1234567890">+1 (234) 567-890</a></p>
                </div>
              </div>
              
              <div className="info-item">
                <div className="info-icon">
                  <FaMapMarkerAlt />
                </div>
                <div className="info-content">
                  <h3>Location</h3>
                  <p>Bengaluru, India</p>
                </div>
              </div>
            </div>
            
            <div className="contact-social">
              <h3>Connect With Me</h3>
              <div className="social-links">
                <a href="https://twitter.com/hemantsinghsidar" className="social-link" target="_blank" rel="noopener noreferrer" aria-label="Twitter">
                  <FaTwitter />
                </a>
                <a href="https://www.reddit.com/user/hemantsinghsidar" className="social-link" target="_blank" rel="noopener noreferrer" aria-label="Reddit">
                  <FaReddit />
                </a>
                <a href="https://www.linkedin.com/in/hemantsinghsidar" className="social-link" target="_blank" rel="noopener noreferrer" aria-label="LinkedIn">
                  <FaLinkedinIn />
                </a>
                <a href="https://huggingface.co/hemantsinghsidar" className="social-link" target="_blank" rel="noopener noreferrer" aria-label="Hugging Face">
                  <SiOpenai />
                </a>
                <a href="https://github.com/hemantsinghsidar" className="social-link" target="_blank" rel="noopener noreferrer" aria-label="GitHub">
                  <FaGithub />
                </a>
              </div>
            </div>
          </div>
          
          <div className="contact-form-container">
            <h2>Send Me a Message</h2>
            
            {formStatus && (
              <div className={`form-message ${formStatus.type}`}>
                {formStatus.message}
              </div>
            )}
            
            <form className="contact-form" onSubmit={handleSubmit}>
              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="name">Your Name</label>
                  <input
                    type="text"
                    id="name"
                    name="name"
                    value={formData.name}
                    onChange={handleChange}
                    required
                    disabled={isSubmitting}
                  />
                </div>
                
                <div className="form-group">
                  <label htmlFor="email">Your Email</label>
                  <input
                    type="email"
                    id="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    required
                    disabled={isSubmitting}
                  />
                </div>
              </div>
              
              <div className="form-group">
                <label htmlFor="subject">Subject</label>
                <input
                  type="text"
                  id="subject"
                  name="subject"
                  value={formData.subject}
                  onChange={handleChange}
                  required
                  disabled={isSubmitting}
                />
              </div>
              
              <div className="form-group">
                <label htmlFor="message">Your Message</label>
                <textarea
                  id="message"
                  name="message"
                  rows="5"
                  value={formData.message}
                  onChange={handleChange}
                  required
                  disabled={isSubmitting}
                ></textarea>
              </div>
              
              <button type="submit" className="btn btn-primary" disabled={isSubmitting}>
                {isSubmitting ? 'Sending...' : 'Send Message'}
              </button>
            </form>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Contact; 