/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */

import { ExtraFormData } from '../../query';
import { JsonObject } from '../..';

export type HandlerFunction = (...args: unknown[]) => void;

export enum Behavior {
  INTERACTIVE_CHART = 'INTERACTIVE_CHART',
  NATIVE_FILTER = 'NATIVE_FILTER',
}

export enum AppSection {
  EXPLORE = 'EXPLORE',
  DASHBOARD = 'DASHBOARD',
  FILTER_BAR = 'FILTER_BAR',
  FILTER_CONFIG_MODAL = 'FILTER_CONFIG_MODAL',
  EMBEDDED = 'EMBEDDED',
}

export type FilterState = { value?: any; [key: string]: any };

export type DataMask = {
  extraFormData?: ExtraFormData;
  filterState?: FilterState;
  ownState?: JsonObject;
};

export type SetDataMaskHook = {
  ({ filterState, extraFormData, ownState }: DataMask): void;
};

export interface PlainObject {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  [key: string]: any;
}

export enum ChartLabel {
  VERIFIED = 'VERIFIED',
  DEPRECATED = 'DEPRECATED',
  FEATURED = 'FEATURED',
}

export const ChartLabelWeight = {
  [ChartLabel.DEPRECATED]: {
    weight: -0.1,
  },
  [ChartLabel.VERIFIED]: {
    weight: 0.2,
  },
  [ChartLabel.FEATURED]: {
    weight: 0.1,
  },
};

export default {};
