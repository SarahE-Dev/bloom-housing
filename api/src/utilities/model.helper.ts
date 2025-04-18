import { HttpService } from '@nestjs/axios';
import { firstValueFrom } from 'rxjs';

export interface ApplicationDto {
  income?: string;
  householdSize?: number;
  housingStatus?: string;
  incomeVouchers?: boolean;
  householdExpectingChanges?: boolean;
  householdStudent?: boolean;
}

export interface ModelFeatures {
  income: number;
  household_size: number;
  housing_status: number;
  income_vouchers: number;
  household_expecting_changes: number;
  household_student: number;
}

// This logic will change as our model is training on real data, and what we need to give the model changes. I just wanted to split the logic into separate functions and move to separate file.

export const mapDtoToModelFeatures = (dto: ApplicationDto): ModelFeatures => {
  return {
    income: parseFloat(dto.income?.replace(/[^0-9.]/g, '')) || 0,
    household_size: dto.householdSize || 1,
    housing_status: mapHousingStatus(dto.housingStatus),
    income_vouchers: dto.incomeVouchers ? 1 : 0,
    household_expecting_changes: dto.householdExpectingChanges ? 1 : 0,
    household_student: dto.householdStudent ? 1 : 0,
  };
};

const mapHousingStatus = (status?: string): number => {
  switch (status) {
    case 'homeless':
      return 0;
    case 'renting':
      return 1;
    case 'owning':
      return 2;
    default:
      return 2;
  }
};

export const getModelPrediction = async (
  httpService: HttpService,
  features: ModelFeatures,
): Promise<number> => {
  try {
    const response = await firstValueFrom(
      httpService.post('http://localhost:5000/predict', { features }),
    );
    return response.data.risk_score;
  } catch (error) {
    console.error('Model Prediction failed:', error.message);
    throw new Error('Model prediction service unavailable');
  }
};
