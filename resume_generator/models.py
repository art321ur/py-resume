"""Pydantic models for resume schema."""
from typing import List, Optional

from pydantic import BaseModel


class Location(BaseModel):
    """Location information."""
    address: Optional[str] = None
    postalCode: Optional[str] = None
    city: Optional[str] = None
    countryCode: Optional[str] = None
    region: Optional[str] = None


class Profile(BaseModel):
    """Social media profile."""
    network: Optional[str] = None
    username: Optional[str] = None
    url: Optional[str] = None


class Basics(BaseModel):
    """Basic information."""
    name: str
    label: Optional[str] = None
    picture: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    summary: Optional[str] = None
    location: Optional[Location] = None
    profiles: Optional[List[Profile]] = None


class AdditionalItem(BaseModel):
    """Additional technology/skill item."""
    title: str
    tech: List[str]


class Work(BaseModel):
    """Work experience."""
    name: Optional[str] = None
    position: Optional[str] = None
    website: Optional[str] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    summary: Optional[str] = None
    highlights: Optional[List[str]] = None
    additional: Optional[List[AdditionalItem]] = None


class Volunteer(BaseModel):
    """Volunteer experience."""
    organization: Optional[str] = None
    position: Optional[str] = None
    website: Optional[str] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    summary: Optional[str] = None
    highlights: Optional[List[str]] = None


class Education(BaseModel):
    """Education information."""
    institution: Optional[str] = None
    area: Optional[str] = None
    studyType: Optional[str] = None
    location: Optional[str] = None
    specialization: Optional[str] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    gpa: Optional[str] = None
    courses: Optional[List[str]] = None


class Skill(BaseModel):
    """Skill information."""
    category: Optional[str] = None
    name: str
    rating: Optional[int] = None


class Language(BaseModel):
    """Language information."""
    language: str
    rating: Optional[int] = None


class Interest(BaseModel):
    """Interest/hobby information."""
    name: str
    keywords: Optional[List[str]] = None


class PortfolioItem(BaseModel):
    """Portfolio entry supporting Markdown descriptions."""
    name: str
    description: Optional[str] = None
    url: Optional[str] = None


class Resume(BaseModel):
    """Complete resume schema."""
    basics: Basics
    work: Optional[List[Work]] = None
    volunteer: Optional[List[Volunteer]] = None
    education: Optional[List[Education]] = None
    skills: Optional[List[Skill]] = None
    languages: Optional[List[Language]] = None
    interests: Optional[List[Interest]] = None
    awards: Optional[List[dict]] = None
    publications: Optional[List[dict]] = None
    references: Optional[List[dict]] = None
    portfolio: Optional[List[PortfolioItem]] = None
    cvFooter: Optional[str] = None
