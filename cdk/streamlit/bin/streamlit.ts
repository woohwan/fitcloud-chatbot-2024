#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { StreamlitStack } from '../lib/streamlit-stack';

const app = new cdk.App();
new StreamlitStack(app, 'StreamlitStack', {
  
});