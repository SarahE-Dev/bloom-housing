import { ApiProperty } from '@nestjs/swagger';
import { Expose } from 'class-transformer';
import { IsBoolean, IsNumber } from 'class-validator';
import { ValidationsGroupsEnum } from '../../enums/shared/validation-groups-enum';
import { AbstractDTO } from '../shared/abstract.dto';

export class Risk extends AbstractDTO {
  @Expose()
  @IsNumber({}, { groups: [ValidationsGroupsEnum.default] })
  @ApiProperty()
  riskProbability: number;

  @Expose()
  @IsBoolean({ groups: [ValidationsGroupsEnum.default] })
  @ApiProperty()
  riskPrediction: boolean;

  @Expose()
  @IsBoolean({ groups: [ValidationsGroupsEnum.default] })
  @ApiProperty()
  veteran: boolean;

  @Expose()
  @IsNumber({}, { groups: [ValidationsGroupsEnum.default] })
  @ApiProperty()
  income: number;

  @Expose()
  @IsBoolean({ groups: [ValidationsGroupsEnum.default] })
  @ApiProperty()
  disabled: boolean;

  @Expose()
  @IsNumber({}, { groups: [ValidationsGroupsEnum.default] })
  @ApiProperty()
  numPeople: number;

  @Expose()
  @IsNumber({}, { groups: [ValidationsGroupsEnum.default] })
  @ApiProperty()
  age: number;

  @Expose()
  @IsBoolean({ groups: [ValidationsGroupsEnum.default] })
  @ApiProperty()
  benefits: boolean;

  @Expose()
  @IsNumber({}, { groups: [ValidationsGroupsEnum.default] })
  @ApiProperty()
  applicationId: string;
} 