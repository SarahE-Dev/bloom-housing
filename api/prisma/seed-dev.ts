import {
  LanguagesEnum,
  ListingsStatusEnum,
  MultiselectQuestionsApplicationSectionEnum,
  PrismaClient,
} from '@prisma/client';
import { userFactory } from './seed-helpers/user-factory';
import { jurisdictionFactory } from './seed-helpers/jurisdiction-factory';
import { amiChartFactory } from './seed-helpers/ami-chart-factory';
import { multiselectQuestionFactory } from './seed-helpers/multiselect-question-factory';
import { listingFactory } from './seed-helpers/listing-factory';
import { unitTypeFactoryAll } from './seed-helpers/unit-type-factory';
import { randomName } from './seed-helpers/word-generator';
import { randomInt } from 'node:crypto';
import { applicationFactory } from './seed-helpers/application-factory';
import { translationFactory } from './seed-helpers/translation-factory';
import { reservedCommunityTypeFactoryAll } from './seed-helpers/reserved-community-type-factory';
import { householdMemberFactoryMany } from './seed-helpers/household-member-factory';
import { APPLICATIONS_PER_LISTINGS, LISTINGS_TO_SEED } from './constants';
import { featureFlagFactory } from './seed-helpers/feature-flag-factory';

const listingStatusEnumArray = Object.values(ListingsStatusEnum);

const createMultiselect = async (
  jurisdictionId: string,
  prismaClient: PrismaClient,
) => {
  const multiSelectQuestions = [...new Array(4)].map(async (_, index) => {
    return await prismaClient.multiselectQuestions.create({
      data: multiselectQuestionFactory(jurisdictionId, {
        multiselectQuestion: {
          text: randomName(),
          applicationSection:
            index % 2
              ? MultiselectQuestionsApplicationSectionEnum.preferences
              : MultiselectQuestionsApplicationSectionEnum.programs,
        },
        optOut: index > 1,
      }),
    });
  });
  return multiSelectQuestions;
};

export const devSeeding = async (
  prismaClient: PrismaClient,
  jurisdictionName?: string,
) => {
  const jurisdiction = await prismaClient.jurisdictions.create({
    data: {
      ...jurisdictionFactory(jurisdictionName),
      allowSingleUseCodeLogin: false,
    },
  });
  await prismaClient.userAccounts.upsert({
    where: { email: 'admin@example.com' },
    update: {},
    create: await userFactory({
      roles: { isAdmin: true },
      email: 'admin@example.com',
      confirmedAt: new Date(),
      jurisdictionIds: [jurisdiction.id],
      acceptedTerms: true,
      password: 'abcdef',
    }),
  });
  await prismaClient.userAccounts.upsert({
    where: { email: 'public-user@example.com' },
    update: {},
    create: await userFactory({
      email: 'public-user@example.com',
      confirmedAt: new Date(),
      jurisdictionIds: [jurisdiction.id],
      password: 'abcdef',
    }),
  });
  await prismaClient.userAccounts.upsert({
    where: { email: 'jurisdiction-admin@example.com' },
    update: {},
    create: await userFactory({
      roles: { isJurisdictionalAdmin: true },
      email: 'jurisdiction-admin@example.com',
      confirmedAt: new Date(),
      jurisdictionIds: [jurisdiction.id],
    }),
  });
  // add jurisdiction specific translations and default ones
  await prismaClient.translations.create({
    data: translationFactory(jurisdiction.id, jurisdiction.name),
  });
  await prismaClient.translations.create({
    data: translationFactory(undefined, undefined, LanguagesEnum.es),
  });
  await prismaClient.translations.create({
    data: translationFactory(),
  });
  const unitTypes = await unitTypeFactoryAll(prismaClient);
  const amiChart = await prismaClient.amiChart.create({
    data: amiChartFactory(10, jurisdiction.id),
  });
  const multiselectQuestions = await Promise.all(
    await createMultiselect(jurisdiction.id, prismaClient),
  );

  // Create feature flags if they don't exist
  const existingFlags = await prismaClient.featureFlags.findMany({
    where: {
      name: {
        in: ['enableRegions', 'enableIsVerified', 'enableSection8Question']
      }
    }
  });
  const existingFlagNames = new Set(existingFlags.map(f => f.name));

  if (!existingFlagNames.has('enableRegions')) {
    await prismaClient.featureFlags.create({
      data: featureFlagFactory(
        'enableRegions',
        false,
        'When true, the region can be defined for the building address',
        [jurisdiction.id],
      ),
    });
  }

  await reservedCommunityTypeFactoryAll(jurisdiction.id, prismaClient);

  if (!existingFlagNames.has('enableIsVerified')) {
    await prismaClient.featureFlags.create({
      data: featureFlagFactory(
        'enableIsVerified',
        false,
        'When true, the listing can ba have its contents manually verified by a user',
        [jurisdiction.id],
      ),
    });
  }

  if (!existingFlagNames.has('enableSection8Question')) {
    await prismaClient.featureFlags.create({
      data: featureFlagFactory(
        'enableSection8Question',
        false,
        'When true, the Section 8 listing data will be visible',
        [jurisdiction.id],
      ),
    });
  }

  for (let index = 0; index < LISTINGS_TO_SEED; index++) {
    const applications = [];

    for (let j = 0; j < APPLICATIONS_PER_LISTINGS; j++) {
      const householdSize = randomInt(1, 6);
      const householdMembers = await householdMemberFactoryMany(
        householdSize - 1,
      );
      const app = await applicationFactory({
        householdSize,
        unitTypeId: unitTypes[randomInt(0, 5)].id,
        householdMember: householdMembers,
        multiselectQuestions,
      });
      applications.push(app);
    }

    const listing = await listingFactory(jurisdiction.id, prismaClient, {
      amiChart: amiChart,
      numberOfUnits: index + 1,
      includeBuildingFeatures: index > 1,
      includeEligibilityRules: index > 2,
      status:
        index < 4
          ? ListingsStatusEnum.active
          : listingStatusEnumArray[
              index - 3 < listingStatusEnumArray.length
                ? index - 3
                : randomInt(listingStatusEnumArray.length - 1)
            ],
      multiselectQuestions:
        index > 0 ? multiselectQuestions.slice(0, index - 1) : [],
      applications,
      digitalApp: !!(index % 2),
    });
    await prismaClient.listings.create({
      data: listing,
    });
  }
};
