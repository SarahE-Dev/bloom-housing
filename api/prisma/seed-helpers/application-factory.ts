import {
  Prisma,
  IncomePeriodEnum,
  ApplicationStatusEnum,
  ApplicationSubmissionTypeEnum,
  MultiselectQuestions,
  YesNoEnum,
  MultiselectQuestionsApplicationSectionEnum,
} from '@prisma/client';
import { generateConfirmationCode } from '../../src/utilities/applications-utilities';
import { addressFactory } from './address-factory';
import { randomNoun } from './word-generator';
import {
  randomBirthDay,
  randomBirthMonth,
  randomBirthYear,
} from './number-generator';
import { preferenceFactory } from './application-preference-factory';
import { demographicsFactory } from './demographic-factory';
import { alternateContactFactory } from './alternate-contact-factory';
import { randomBoolean } from './boolean-generator';

export const applicationFactory = async (optionalParams?: {
  householdSize?: number;
  unitTypeId?: string;
  applicant?: Prisma.ApplicantCreateWithoutApplicationsInput;
  overrides?: Prisma.ApplicationsCreateInput;
  listingId?: string;
  householdMember?: Prisma.HouseholdMemberCreateWithoutApplicationsInput[];
  demographics?: Prisma.DemographicsCreateWithoutApplicationsInput;
  multiselectQuestions?: Partial<MultiselectQuestions>[];
  userId?: string;
  submissionType?: ApplicationSubmissionTypeEnum;
}): Promise<Prisma.ApplicationsCreateInput> => {
  let preferredUnitTypes: Prisma.UnitTypesCreateNestedManyWithoutApplicationsInput;
  if (optionalParams?.unitTypeId) {
    preferredUnitTypes = {
      connect: [
        {
          id: optionalParams.unitTypeId,
        },
      ],
    };
  }
  const demographics = await demographicsFactory();
  const additionalPhone = randomBoolean();
  return {
    confirmationCode: generateConfirmationCode(),
    applicant: { create: applicantFactory(optionalParams?.applicant) },
    appUrl: '',
    status: ApplicationStatusEnum.submitted,
    submissionType:
      optionalParams?.submissionType ??
      ApplicationSubmissionTypeEnum.electronical,
    submissionDate: new Date(),
    householdSize: optionalParams?.householdSize ?? 1,
    income: '40000',
    incomePeriod: randomBoolean()
      ? IncomePeriodEnum.perYear
      : IncomePeriodEnum.perMonth,
    preferences: preferenceFactory(
      optionalParams?.multiselectQuestions
        ? optionalParams.multiselectQuestions.filter(
            (question) =>
              question.applicationSection ===
              MultiselectQuestionsApplicationSectionEnum.preferences,
          )
        : [],
    ),
    programs: preferenceFactory(
      optionalParams?.multiselectQuestions
        ? optionalParams.multiselectQuestions.filter(
            (question) =>
              question.applicationSection ===
              MultiselectQuestionsApplicationSectionEnum.programs,
          )
        : [],
    ),
    preferredUnitTypes,
    sendMailToMailingAddress: true,
    applicationsMailingAddress: {
      create: addressFactory(),
    },
    listings: optionalParams?.listingId
      ? {
          connect: {
            id: optionalParams?.listingId,
          },
        }
      : undefined,
    ...optionalParams?.overrides,
    householdMember: optionalParams?.householdMember
      ? {
          create: optionalParams.householdMember,
        }
      : undefined,
    demographics: {
      create: demographics,
    },
    alternateContact: { create: alternateContactFactory() },
    userAccounts: optionalParams?.userId
      ? {
          connect: {
            id: optionalParams.userId,
          },
        }
      : undefined,
    incomeVouchers: randomBoolean(),
    additionalPhoneNumber: additionalPhone ? '(456) 456-4564' : undefined,
    additionalPhone,
    additionalPhoneNumberType: additionalPhone ? 'cell' : undefined,
    risk: {
      create: {
        riskProbability: (() => {
          const rand = Math.random();
          if (rand < 0.6) return Math.random() * 0.4;
          if (rand < 0.9) return 0.4 + (Math.random() * 0.3);
          return 0.7 + (Math.random() * 0.3);
        })(),
        riskPrediction: Math.random() > 0.5,
        veteran: Math.random() < 0.07,
        income: (() => {
          const baseIncome = 30000;
          const multiplier = Math.exp(Math.random() * 2);
          return Math.floor(baseIncome * multiplier);
        })(),
        disabled: Math.random() < 0.15,
        numPeople: Math.floor(Math.random() * Math.random() * 6) + 1,
        age: (() => {
          const rand = Math.random();
          if (rand < 0.25) return Math.floor(18 + Math.random() * 12);
          if (rand < 0.7) return Math.floor(31 + Math.random() * 19);
          if (rand < 0.95) return Math.floor(51 + Math.random() * 19);
          return Math.floor(71 + Math.random() * 20);
        })(),
        benefits: Math.random() < 0.2,
      },
    },
  };
};

export const applicantFactory = (
  overrides?: Prisma.ApplicantCreateWithoutApplicationsInput,
): Prisma.ApplicantCreateWithoutApplicationsInput => {
  const firstName = randomNoun();
  const lastName = randomNoun();
  return {
    firstName: firstName,
    middleName: randomBoolean() ? randomNoun() : undefined,
    lastName: lastName,
    emailAddress: `${firstName}.${lastName}@example.com`,
    noEmail: false,
    phoneNumber: '(123) 123-1231',
    phoneNumberType: 'home',
    noPhone: false,
    workInRegion: YesNoEnum.no,
    birthDay: randomBirthDay(), // no zeros
    birthMonth: randomBirthMonth(), // no zeros
    birthYear: randomBirthYear(),
    applicantAddress: {
      create: addressFactory(),
    },
    applicantWorkAddress: {
      create: addressFactory(),
    },
    ...overrides,
  };
};
