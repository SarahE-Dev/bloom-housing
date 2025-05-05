import React, { useContext, useEffect, useMemo } from "react"
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
import { useFormConductor } from "../../../lib/hooks"

const ApplicationConfirmation = () => {
  const { application, listing } = useContext(AppSubmissionContext)
  const { initialStateLoaded, profile } = useContext(AuthContext)
  const router = useRouter()

  const imageUrl = imageUrlFromListing(listing, parseInt(process.env.listingPhotoSize))[0]
  // load model prediction result from local storage
  const riskPrediction = localStorage.getItem("riskPrediction");
  

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
          {/*Add resources list based on model prediction result being at risk or not at risk*/}
          {riskPrediction && (
  <CardSection divider="inset">
    <Heading priority={2} size="lg" className="mb-4 text-black">
      {t("application.review.confirmation.supportiveServices")}
    </Heading>

    <div className="markdown markdown-informational space-y-4 text-base leading-relaxed">
      {riskPrediction === "At risk" ? (
        <>
          <p>
            Based on your responses, we’ve gathered some helpful resources that may offer immediate support and guidance.
            These programs are available to assist individuals and families experiencing housing-related challenges.
          </p>

          <p className="font-semibold">Recommended Support Services</p>

          <ul className="list-disc pl-6 space-y-4">
            <li>
              <a
                href="https://www.alamedacountysocialservices.org/our-services/Shelter-and-Housing/Other-Support/emergency-shelters"
                target="_blank"
                rel="noopener noreferrer"
                className="underline"
              >
                Emergency Shelters & Hotel Vouchers
              </a>
              : Temporary shelter options for those in urgent need of a safe place to stay.
              <br />
              Call 2-1-1 or text your ZIP code to 898211
            </li>
            <li>
              <a
                href="https://homelessness.acgov.org/ac-housing-resource.page"
                target="_blank"
                rel="noopener noreferrer"
                className="underline"
              >
                Safe Parking Program (San Leandro Fairmont Campus)
              </a>
              : A secure overnight option for those living in vehicles, with access to support services.
              <br />
              Call 2-1-1 for availability and intake
            </li>
            <li>
              <a
                href="https://www.achch.org/get-help.html"
                target="_blank"
                rel="noopener noreferrer"
                className="underline"
              >
                Crisis Support Services (Mental Health Hotline)
              </a>
              : 24/7 confidential help for emotional or mental health support.
              <br />
              Call (800) 309-2131
            </li>
            <li>
              <a
                href="https://www.achch.org/winter-emergency-resources.html"
                target="_blank"
                rel="noopener noreferrer"
                className="underline"
              >
                Winter Emergency Resources & Warming Centers
              </a>
              : Stay warm and safe with seasonal resources during colder months.
            </li>
            <li>
              <a
                href="https://www.alamedaca.gov/CITYWIDE-PROJECTS/Programs-and-Services-Addressing-Homelessness"
                target="_blank"
                rel="noopener noreferrer"
                className="underline"
              >
                Alameda Homeless Hotline
              </a>
              : Helps connect you with food, shelter, and health services in your area.
              <br />
              Call (510) 522-4663 or 2-1-1 after hours
            </li>
          </ul>
        </>
      ) : (
        <>
          <p>
            Based on your application, you may benefit from services designed to support long-term housing stability and overall well-being. We’ve gathered a few options that may be a good fit for you or your family.
          </p>

          <p className="font-semibold">Recommended Support Services</p>

          <ul className="list-disc pl-6 space-y-4">
            <li>
              <a
                href="https://alamedakids.org/resource-directory/search-resource-directory.php?by=service&id=18"
                target="_blank"
                rel="noopener noreferrer"
                className="underline"
              >
                Coordinated Entry System (CES)
              </a>
              : Helps prioritize access to housing and supportive services.
              <br />
              Start by calling 2-1-1
            </li>
            <li>
              <a
                href="https://www.alamedacountysocialservices.org/our-services/Shelter-and-Housing/CalWORKs-housing-assistance/index"
                target="_blank"
                rel="noopener noreferrer"
                className="underline"
              >
                CalWORKs Housing Assistance
              </a>
              : Financial assistance for rent, utilities, and deposits for eligible families.
              <br />
              Apply by calling (510) 263-2420 or 1-888-999-4772
            </li>
            <li>
              <a
                href="https://homelessness.acgov.org/housing-community-supports.page"
                target="_blank"
                rel="noopener noreferrer"
                className="underline"
              >
                CalAIM Housing Community Supports
              </a>
              : Combines health coverage with housing-related support like tenancy navigation.
            </li>
            <li>
              <a
                href="https://bayareacs.org/alameda-county/"
                target="_blank"
                rel="noopener noreferrer"
                className="underline"
              >
                Bay Area Community Services (BACS)
              </a>
              : Offers mental health and housing support with individualized case management.
              <br />
              Call 1-800-491-9099
            </li>
            <li>
              <a
                href="https://www.alamedacounty.info/food-banks"
                target="_blank"
                rel="noopener noreferrer"
                className="underline"
              >
                Alameda County Community Food Bank
              </a>
              : Access groceries and meal programs for individuals and families.
            </li>
          </ul>
        </>
      )}
    </div>
  </CardSection>
)}






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
