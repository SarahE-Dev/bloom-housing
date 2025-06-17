import React, { useContext, useEffect, useMemo, useState } from "react"
import { useRouter } from "next/router"
import Markdown from "markdown-to-jsx"
import { t, ApplicationTimeline } from "@bloom-housing/ui-components"
import { CardSection } from "@bloom-housing/ui-seeds/src/blocks/Card"
import {
  imageUrlFromListing,
  PageView,
  pushGtmEvent,
  AuthContext,
  BloomCard,
} from "@bloom-housing/shared-helpers"
import { Button, Heading, Link } from "@bloom-housing/ui-seeds"
import FormsLayout from "../../../layouts/forms"
import { AppSubmissionContext } from "../../../lib/applications/AppSubmissionContext"
import { UserStatus } from "../../../lib/constants"
import { ReviewOrderTypeEnum } from "@bloom-housing/shared-helpers/src/types/backend-swagger"

export const atRiskResources = [
  {
    label: "Emergency Shelters & Hotel Vouchers",
    href: "https://www.alamedacountysocialservices.org/our-services/Shelter-and-Housing/Other-Support/emergency-shelters",
    description:
      "Temporary shelter options for those in urgent need of a safe place to stay. Call 2-1-1 or text your ZIP code to 898211",
  },
  {
    label: "Safe Parking Program (San Leandro Fairmont Campus)",
    href: "https://homelessness.acgov.org/ac-housing-resource.page",
    description:
      "A secure overnight option for those living in vehicles, with access to support services. Call 2-1-1 for availability and intake",
  },
  {
    label: "Crisis Support Services (Mental Health Hotline)",
    href: "https://www.achch.org/get-help.html",
    description:
      "24/7 confidential help for emotional or mental health support. Call (800) 309-2131",
  },
  {
    label: "Winter Emergency Resources & Warming Centers",
    href: "https://www.achch.org/winter-emergency-resources.html",
    description: "Stay warm and safe with seasonal resources during colder months.",
  },
  {
    label: "Alameda Homeless Hotline",
    href: "https://www.alamedaca.gov/CITYWIDE-PROJECTS/Programs-and-Services-Addressing-Homelessness",
    description:
      "Helps connect you with food, shelter, and health services in your area. Call (510) 522-4663 or 2-1-1 after hours",
  },
]


export const notAtRiskResources = [
  {
    label: "Coordinated Entry System (CES)",
    href: "https://alamedakids.org/resource-directory/search-resource-directory.php?by=service&id=18",
    description:
      "Helps prioritize access to housing and supportive services. Start by calling 2-1-1",
  },
  {
    label: "CalWORKs Housing Assistance",
    href: "https://www.alamedacountysocialservices.org/our-services/Shelter-and-Housing/CalWORKs-housing-assistance/index",
    description:
      "Financial assistance for rent, utilities, and deposits for eligible families. Apply by calling (510) 263-2420 or 1-888-999-4772",
  },
  {
    label: "CalAIM Housing Community Supports",
    href: "https://homelessness.acgov.org/housing-community-supports.page",
    description:
      "Combines health coverage with housing-related support like tenancy navigation.",
  },
  {
    label: "Bay Area Community Services (BACS)",
    href: "https://bayareacs.org/alameda-county/",
    description:
      "Offers mental health and housing support with individualized case management. Call 1-800-491-9099",
  },
  {
    label: "Alameda County Community Food Bank",
    href: "https://www.alamedacounty.info/food-banks",
    description:
      "Access groceries and meal programs for individuals and families.",
  },
]

const ApplicationConfirmation = () => {
  const { application, listing } = useContext(AppSubmissionContext)
  const { initialStateLoaded, profile } = useContext(AuthContext)
  const [riskPrediction, setRiskPrediction] = useState<string | null>(null)
  const router = useRouter()

  const imageUrl = imageUrlFromListing(listing, parseInt(process.env.listingPhotoSize || "300"))[0]

  const GA_ID = "G-JTD2F2W9RM"
  console.log("Google Analytics ID:", GA_ID)

  // Inject GA script only once
  useEffect(() => {
    if (!GA_ID) return

    const script1 = document.createElement("script")
    script1.src = `https://www.googletagmanager.com/gtag/js?id=${GA_ID}`
    script1.async = true
    document.head.appendChild(script1)

    const script2 = document.createElement("script")
    script2.innerHTML = `
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());
      gtag('config', '${GA_ID}', { debug_mode: false });
    `
    document.head.appendChild(script2)
  }, [GA_ID])

  // Load risk prediction from localStorage
  useEffect(() => {
    if (typeof window !== "undefined") {
      const storedPrediction = localStorage.getItem("riskPrediction")
      setRiskPrediction(storedPrediction)
    }
  }, [])

  // Track outbound clicks
  const handleOutboundClick = (url: string) => (e: React.MouseEvent<HTMLAnchorElement>) => {
    e.preventDefault()
    if ((window as any).gtag) {
      ;(window as any).gtag("event", "outbound_link_click", {
        event_category: "outbound",
        event_label: url,
        transport_type: "beacon",
      })
    }
    setTimeout(() => {
      window.open(url, "_blank", "noopener,noreferrer")
    }, 200)
  }

  const riskSupportContent = {
    "At risk": {
      intro: (
        <>
          <p>
            Based on your responses, we’ve gathered some helpful resources that may offer immediate
            support and guidance.
          </p>
          <p className="font-semibold">Recommended Support Services</p>
        </>
      ),
      resources: atRiskResources,
    },
    "Not at risk": {
      intro: (
        <>
          <p>
            Based on your application, you may benefit from services designed to support long-term
            housing stability and overall well-being.
          </p>
          <p className="font-semibold">Recommended Support Services</p>
        </>
      ),
      resources: notAtRiskResources,
    },
  }

  const content = useMemo(() => {
    switch (listing?.reviewOrderType) {
      case ReviewOrderTypeEnum.firstComeFirstServe:
        return { text: t("application.review.confirmation.whatHappensNext.fcfs") }
      case ReviewOrderTypeEnum.lottery:
        return { text: t("application.review.confirmation.whatHappensNext.lottery") }
      case ReviewOrderTypeEnum.waitlist:
        return { text: t("application.review.confirmation.whatHappensNext.waitlist") }
      default:
        return { text: "" }
    }
  }, [listing, router.locale])

  return (
    <FormsLayout>
      <BloomCard>
        <>
          <CardSection divider="flush">
            <Heading priority={1} size="2xl">
              {t("application.review.confirmation.title")}
              {listing?.name}
            </Heading>
          </CardSection>

          {imageUrl && <img src={imageUrl} alt={listing?.name} />}

          <CardSection divider="inset">
            <Heading priority={2} size="lg">
              {t("application.review.confirmation.lotteryNumber")}
            </Heading>
            <p className="font-serif text-2xl my-3">
              {application.confirmationCode || application.id}
            </p>
            <p>{t("application.review.confirmation.pleaseWriteNumber")}</p>
          </CardSection>

          <CardSection divider="inset">
            <div className="markdown markdown-informational">
              <ApplicationTimeline />
              <Markdown options={{ disableParsingRawHTML: true }}>{content.text}</Markdown>
            </div>
          </CardSection>

          {riskPrediction && riskSupportContent[riskPrediction] && (
            <CardSection divider="inset">
              <Heading priority={2} size="lg" className="mb-4 text-black">
                {t("application.review.confirmation.supportiveServices")}
              </Heading>

              <div className="markdown markdown-informational space-y-4 text-base leading-relaxed">
                {riskSupportContent[riskPrediction].intro}
                <ul className="list-disc pl-6 space-y-4">
                  {riskSupportContent[riskPrediction].resources.map((resource, idx) => (
                    <li key={idx}>
                      <a
                        href={resource.href}
                        onClick={handleOutboundClick(resource.href)}
                        className="underline"
                      >
                        {resource.label}
                      </a>
                      : {resource.description}
                    </li>
                  ))}
                </ul>
              </div>
            </CardSection>
          )}

          <CardSection divider="inset">
            <div className="markdown markdown-informational">
              <Markdown options={{ disableParsingRawHTML: true }}>
                {t("application.review.confirmation.needToMakeUpdates", {
                  agentName: listing?.leasingAgentName || "",
                  agentPhone: listing?.leasingAgentPhone || "",
                  agentEmail: listing?.leasingAgentEmail || "",
                  agentOfficeHours: listing?.leasingAgentOfficeHours || "",
                })}
              </Markdown>
            </div>
          </CardSection>

          {initialStateLoaded && !profile && (
            <>
              <CardSection divider="flush" className="border-none">
                <div className="markdown markdown-informational">
                  <Markdown options={{ disableParsingRawHTML: true }}>
                    {t("application.review.confirmation.createAccount")}
                  </Markdown>
                </div>
              </CardSection>

              <CardSection className="bg-primary-lighter border-none" divider="flush">
                <Button
                  variant="primary"
                  onClick={() => void router.push("/create-account")}
                  id="app-confirmation-create-account"
                >
                  {t("account.createAccount")}
                </Button>
              </CardSection>
            </>
          )}

          <CardSection divider="flush">
            <Link href="/listings">{t("application.review.confirmation.browseMore")}</Link>
          </CardSection>

          <CardSection>
            <Link href="/applications/view">{t("application.review.confirmation.print")}</Link>
          </CardSection>
        </>
      </BloomCard>
    </FormsLayout>
  )
}

export default ApplicationConfirmation
