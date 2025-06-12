import { Prisma, PrismaClient } from '@prisma/client';
import { randomBoolean } from './boolean-generator';
import { randomAdjective, randomName } from './word-generator';
import { featureFlagMap } from '../../src/enums/feature-flags/feature-flags-enum';

export const createAllFeatureFlags = async (prismaClient: PrismaClient) => {
  // First get all existing feature flags
  const existingFlags = await prismaClient.featureFlags.findMany({
    select: { name: true },
  });
  const existingFlagNames = new Set(existingFlags.map(f => f.name));

  // Only create flags that don't exist yet
  const flagsToCreate = featureFlagMap.filter(flag => !existingFlagNames.has(flag.name));
  
  if (flagsToCreate.length > 0) {
    await prismaClient.featureFlags.createMany({
      data: flagsToCreate.map((flag) => {
        return { ...flag, active: true };
      }),
      skipDuplicates: true,
    });
  }
};

export const attachJurisdictionToFlags = async (
  jurisdiction: string,
  featureFlags: string[],
  prismaClient: PrismaClient,
) => {
  for (const flag of featureFlags) {
    await prismaClient.featureFlags.update({
      where: {
        name: flag,
      },
      data: {
        jurisdictions: {
          connect: {
            id: jurisdiction,
          },
        },
      },
    });
  }
};

export const featureFlagFactory = (
  name = randomName(),
  active = randomBoolean(),
  description = `${randomAdjective()} feature flag`,
  jurisdictionIds?: string[],
): Prisma.FeatureFlagsCreateInput => ({
  name: name,
  description: description,
  active: active,
  jurisdictions: jurisdictionIds
    ? {
        connect: jurisdictionIds.map((jurisdiction) => {
          return {
            id: jurisdiction,
          };
        }),
      }
    : undefined,
});
