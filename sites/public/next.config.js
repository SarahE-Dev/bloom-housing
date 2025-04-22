/* eslint-env node */
/* eslint-disable @typescript-eslint/no-var-requires */

const withBundleAnalyzer = require("@next/bundle-analyzer")({
  enabled: process.env.ANALYZE === "true",
})

if (process.env.NODE_ENV !== "production") {
  require("dotenv").config()
}

// Set up app-wide constants
let BACKEND_API_BASE = "http://localhost:3100"
if (process.env.INCOMING_HOOK_BODY?.startsWith("http")) {
  BACKEND_API_BASE = decodeURIComponent(process.env.INCOMING_HOOK_BODY)
} else if (process.env.BACKEND_PROXY_BASE) {
  BACKEND_API_BASE = process.env.BACKEND_PROXY_BASE
} else if (process.env.BACKEND_API_BASE) {
  BACKEND_API_BASE = process.env.BACKEND_API_BASE
}

const LISTINGS_QUERY = process.env.LISTINGS_QUERY || "/listings"
console.log(`Using ${BACKEND_API_BASE}${LISTINGS_QUERY} for the listing service.`)

const MAPBOX_TOKEN = process.env.MAPBOX_TOKEN
const HOUSING_COUNSELOR_SERVICE_URL = process.env.HOUSING_COUNSELOR_SERVICE_URL

// Load the Tailwind theme and SASS vars
const bloomTheme = require("./tailwind.config.js")
const tailwindVars = require("@bloom-housing/ui-components/tailwind.tosass.js")(bloomTheme)

module.exports = withBundleAnalyzer({
  env: {
    backendApiBase: BACKEND_API_BASE,
    listingServiceUrl: BACKEND_API_BASE + LISTINGS_QUERY,
    listingPhotoSize: process.env.LISTING_PHOTO_SIZE || "1302",
    mapBoxToken: MAPBOX_TOKEN,
    housingCounselorServiceUrl: HOUSING_COUNSELOR_SERVICE_URL,
    gtmKey: process.env.GTM_KEY || "",
    idleTimeout: process.env.IDLE_TIMEOUT || "300000",
    jurisdictionName: process.env.JURISDICTION_NAME || "",
    cacheRevalidate: (process.env.CACHE_REVALIDATE || "60").toString(), // ✅ Stringified
    cloudinaryCloudName: process.env.CLOUDINARY_CLOUD_NAME || "",

    // ✅ Stringify booleans
    showPublicLottery: (process.env.SHOW_PUBLIC_LOTTERY === "TRUE").toString(),
    showNewSeedsDesigns: (process.env.SHOW_NEW_SEEDS_DESIGNS === "TRUE").toString(),
    showMandatedAccounts: (process.env.SHOW_MANDATED_ACCOUNTS === "TRUE").toString(),
    showPwdless: (process.env.SHOW_PWDLESS === "TRUE").toString(),

    maintenanceWindow: process.env.MAINTENANCE_WINDOW || "",
    reCaptchaKey: process.env.RECAPTCHA_KEY || "",
    maxClosedListings: process.env.MAX_CLOSED_LISTINGS || "10",
    rtlLanguages: process.env.RTL_LANGUAGES || "ar",
  },
  i18n: {
    locales: process.env.LANGUAGES ? process.env.LANGUAGES.split(",") : ["en"],
    defaultLocale: "en",
  },
  sassOptions: {
    additionalData: tailwindVars,
  },
  transpilePackages: [
    "@bloom-housing/ui-seeds",
    "@bloom-housing/shared-helpers",
    "@bloom-housing/ui-components",
  ],
  webpack: (config) => {
    config.module.rules.push({
      test: /\.md$/,
      type: "asset/source",
    })

    return config
  },
  // Uncomment below before building when using symlink for UI-C
  // experimental: { esmExternals: "loose" },
})

if (process.env.SENTRY_ORG) {
  const { withSentryConfig } = require("@sentry/nextjs")

  module.exports = withSentryConfig(
    module.exports,
    {
      silent: true,
      org: process.env.SENTRY_ORG,
      project: "public",
    },
    {
      widenClientFileUpload: true,
      transpileClientSDK: true,
      tunnelRoute: "/monitoring",
      hideSourceMaps: true,
      disableLogger: true,
    }
  )
}
