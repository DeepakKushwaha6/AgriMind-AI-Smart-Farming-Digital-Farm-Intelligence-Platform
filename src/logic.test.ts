import test from 'node:test';
import assert from 'node:assert/strict';

// Test 1: Regional unit conversions
function convertRegionalUnits(value: number, unit: string) {
  let acres = value;
  if (unit === 'katha_jh') acres = value / 32;
  else if (unit === 'bigha_jh') acres = value / 1.6;
  else if (unit === 'decimal') acres = value / 100;
  return {
    acres: Math.round(acres * 100) / 100,
    hectares: Math.round((acres / 2.471) * 100) / 100,
    katha: Math.round(acres * 32 * 10) / 10
  };
}

test('regional land unit conversion: 64 Katha in Jharkhand equals exactly 2.00 Acres', () => {
  const result = convertRegionalUnits(64, 'katha_jh');
  assert.equal(result.acres, 2.0);
  assert.equal(result.hectares, 0.81);
  assert.equal(result.katha, 64.0);
});

// Test 2: Net realisation calculation
function calculateNetRealisation(qtyQtl: number, modalPrice: number, distanceKm: number) {
  const gross = qtyQtl * modalPrice;
  const transport = qtyQtl * (distanceKm * 0.9);
  const handling = qtyQtl * 20.0;
  const commission = gross * 0.01;
  const totalDeductions = transport + handling + commission;
  const net = gross - totalDeductions;
  return {
    gross: Math.round(gross),
    net: Math.round(net),
    netPerQtl: Math.round(net / qtyQtl)
  };
}

test('mandi net realisation: transport and handling are accurately deducted', () => {
  // 25 Qtl @ 2350, 12km local transport (270) + 20 handling (500) + 1% comm (587.5) = 1357.5 deductions
  const res = calculateNetRealisation(25, 2350, 12);
  assert.equal(res.gross, 58750);
  assert.ok(res.net < res.gross);
  assert.equal(res.net, 57393);
  assert.equal(res.netPerQtl, 2296);
});

// Test 3: Key masking
function maskKey(plain: string): string {
  if (!plain) return '';
  if (plain.length <= 6) return '••••';
  return `${plain.slice(0, 3)}••••${plain.slice(-4)}`;
}

test('key masking securely hides secrets', () => {
  assert.equal(maskKey('AIzaSyBlhF1v3r9aXsdZN4byYfNjRqjYokmzlHw'), 'AIz••••zlHw');
  assert.equal(maskKey('sk-or-v1-abcdef1234567890'), 'sk-••••7890');
  assert.equal(maskKey('1234'), '••••');
});
