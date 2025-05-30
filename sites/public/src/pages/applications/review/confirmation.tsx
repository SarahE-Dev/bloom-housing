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
import CustomResults from "../../../components/applications/CustomResults"

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

  const [customQuery, setCustomQuery] = useState("")
  const [loading, setLoading] = useState(false)
  const [customResults, setCustomResults] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  const handleCustomSearch = async () => {
    setLoading(true)
    setError(null)
    setCustomResults(null)

    try {
      const response = await fetch('http://localhost:5001/search', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      setCustomQuery("") 
      setCustomResults(data.results)
    } catch (err: any) {
      setError("Failed to fetch custom search results")
      console.error(err)
    } finally {
      setLoading(false)
    }
  }


  const imageUrl = imageUrlFromListing(listing, parseInt(process.env.listingPhotoSize))[0]

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
            housing stability and overall well-being. We’ve gathered a few options that may be a good
            fit for you or your family.
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
        return {
          text: t("application.review.confirmation.whatHappensNext.fcfs"),
        }
      case ReviewOrderTypeEnum.lottery:
        return {
          text: t("application.review.confirmation.whatHappensNext.lottery"),
        }
      case ReviewOrderTypeEnum.waitlist:
        return {
          text: t("application.review.confirmation.whatHappensNext.waitlist"),
        }
      default:
        return { text: "" }
    }
  }, [listing, router.locale])
 
  useEffect(() => {
    pushGtmEvent<PageView>({
      event: "pageView",
      pageTitle: "Application - Confirmation",
      status: profile ? UserStatus.LoggedIn : UserStatus.NotLoggedIn,
    })
  }, [profile])

  useEffect(() => {
    if (typeof window !== "undefined") {
      const storedPrediction = localStorage.getItem("riskPrediction")
      setRiskPrediction(storedPrediction)
    }
  }, [])

  return (
    <FormsLayout>
      <BloomCard>
        <>
          <CardSection divider={"flush"}>
            <Heading priority={1} size={"2xl"}>
              {t("application.review.confirmation.title")}
              {listing?.name}
            </Heading>
          </CardSection>

          {imageUrl && <img src={imageUrl} alt={listing?.name} />}

          <CardSection divider={"inset"}>
            <Heading priority={2} size="lg">
              {t("application.review.confirmation.lotteryNumber")}
            </Heading>

            <p
              id="confirmationCode"
              className="font-serif text-2xl my-3"
              data-testid={"app-confirmation-id"}
            >
              {application.confirmationCode || application.id}
            </p>
            <p>{t("application.review.confirmation.pleaseWriteNumber")}</p>
          </CardSection>

          <CardSection divider={"inset"}>
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
                      target="_blank"
                      rel="noopener noreferrer"
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
            <Heading priority={2} size="lg" className="mb-4 text-black">
              Is there something else you’re looking for?
            </Heading>
            <div className="space-y-4">
              <input
                type="text"
                value={customQuery}
                onChange={(e) => setCustomQuery(e.target.value)}
                className="w-full p-3 border border-gray-300 rounded text-base"
                placeholder="Describe the help you need..."
              />
              <Button variant="primary" onClick={handleCustomSearch} disabled={loading}>
                {loading ? (
                  <span className="loader border-t-2 border-white rounded-full w-4 h-4 inline-block animate-spin"></span>
                ) : (
                  "Search Resources"
                )}
              </Button>

              {error && <p className="text-red-500">{error}</p>}

              <CustomResults customResults={customResults} loading={loading} />



            </div>
          </CardSection>

                  
          <CardSection divider={"inset"}>
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
            <CardSection divider={"flush"} className={"border-none"}>
              <div className="markdown markdown-informational">
                <Markdown options={{ disableParsingRawHTML: true }}>
                  {t("application.review.confirmation.createAccount")}
                </Markdown>
              </div>
            </CardSection>
          )}

          {initialStateLoaded && !profile && (
            <CardSection className={"bg-primary-lighter border-none"} divider={"flush"}>
              <Button
                variant={"primary"}
                onClick={() => {
                  void router.push("/create-account")
                }}
                id={"app-confirmation-create-account"}
              >
                {t("account.createAccount")}
              </Button>
            </CardSection>
          )}

          <CardSection divider={"flush"}>
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
