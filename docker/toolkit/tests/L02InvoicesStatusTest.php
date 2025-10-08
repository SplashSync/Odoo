<?php

/*
 *  This file is part of SplashSync Project.
 *
 *  Copyright (C) Splash Sync  <www.splashsync.com>
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
 *
 *  For the full copyright and license information, please view the LICENSE
 *  file that was distributed with this source code.
 */

namespace Splash\Toolkit\Tests;

use Exception;
use PHPUnit\Framework\Assert;
use Splash\Core\Dictionary\Objects\Invoice\Status;
use Splash\Validator\Phpunit\TestContext as Context;
use Splash\Validator\Phpunit\TestFields;
use Splash\Validator\Phpunit\TestObjects;
use Splash\Validator\Phpunit\Tests\ObjectCrudTest;
use Splash\Validator\Phpunit\TestSequences;
use Splash\Validator\Services\ObjectDataGenerator as Generator;
use Splash\Validator\SplashTestCase;
use Splash\Validator\Phpunit\Tests\Write\SelectiveWritingTest;

/**
 * Local Test Suite - Verify Writing of Invoices Status
 */
class L02InvoicesStatusTest extends SplashTestCase
{
    const TYPE = "Invoice";

    /**
     * @var string[]
     */
    private static array $objectsIds = array();

    /**
     * Create Invoice Objects for Testing
     *
     * @dataProvider sequencesProvider
     */
    public function testCreateObjects(string $sequence): void
    {
        //====================================================================//
        // Configure Env. for Test Sequence
        TestSequences::configure($sequence);
        //====================================================================//
        // Only if tests on Orders are Allowed
        if (!TestObjects::isAllowed(self::TYPE)) {
            $this->assertTrue(true);

            return;
        }
        //====================================================================//
        // Execute Write Test from Module
        $objectTest = new ObjectCrudTest($sequence, self::TYPE);
        $objectTest
            ->setDatasetOverrides(
                $this->getDatasetOverrides(Status::DRAFT),
                array("state")
            )
            ->executeWriteTest()
        ;
        //====================================================================//
        // Store Order ID for next Tests
        Assert::assertNotEmpty($objectId = Context::objectId());
        Assert::assertIsString($objectId);
        self::$objectsIds[$sequence] = $objectId;
    }

    /**
     * Test Invoice Status on Create
     *
     * @dataProvider statusOnCreateProvider
     */
    public function testStatusOnCreate(string $sequence, string $status, bool $withPayments): void
    {
        //====================================================================//
        // Configure Env. for Test Sequence
        TestSequences::configure($sequence);
        //====================================================================//
        // Only if tests on Orders are Allowed
        if (!TestObjects::isAllowed(self::TYPE)) {
            $this->assertTrue(true);

            return;
        }
        //====================================================================//
        // Execute Write Test from Module
        $objectTest = new ObjectCrudTest($sequence, self::TYPE);
        $objectTest
            ->setDatasetOverrides(
                $this->getDatasetOverrides($status, $withPayments),
                array("state"),
            )
            ->executeWriteTest()
        ;
    }

    /**
     * Test Invoices Status
     *
     * @dataProvider invoiceStatusChangesProvider
     *
     * @throws Exception
     */
    public function testStatusChanges(
        string $sequence,
        string $newStatus,
        string $expectedStatus,
        bool   $withPayment
    ): void {
        //====================================================================//
        // Configure Env. for Test Sequence
        TestSequences::configure($sequence);
        //====================================================================//
        // Only if tests on Orders are Allowed
        if (!TestObjects::isAllowed(self::TYPE)) {
            $this->assertTrue(true);

            return;
        }

        //====================================================================//
        // Prepare Data for Update
        Assert::assertNotEmpty($objectId = self::$objectsIds[$sequence]);
        $datasetOverrides = array_merge(
            array(
                "id" => $objectId,
                "state" => $newStatus
            ),
            $withPayment ? $this->getFakePayments() : array()
        );
        //====================================================================//
        // Execute Write Test from Module
        $objectTest = new ObjectCrudTest($sequence, self::TYPE);
        $objectTest
            ->setWriteTest(SelectiveWritingTest::fromFieldIds(self::TYPE, array("state")))
            ->setDatasetOverrides(
                $datasetOverrides,
                array("state"),
            )
            ->executeWriteTest()
        ;
    }

    /**
     * Data Provider for Test of Invoice Status on Create
     */
    public function statusOnCreateProvider(): array
    {
        $results = array();

        $testedStates = array(
           array("status" => Status::CANCELED, "withPayments" => false),
            array("status" => Status::DRAFT, "withPayments" => false),
            array("status" => Status::PAYMENT_DUE, "withPayments" => false),
            array("status" => Status::COMPLETE, "withPayments" => true),
        );

        foreach ($this->sequencesProvider() as $name => $sequence) {
            foreach ($testedStates as $testedState) {
                $stepName = sprintf("%s->%s", $name, $testedState['status']);
                $results[$stepName] = array_merge($sequence, $testedState);
            }
        }

        return $results;
    }

    /**
     * Data Provider for Test of Invoice Status Changes
     */
    public function invoiceStatusChangesProvider(): array
    {
        $results = array();

        //====================================================================//
        // Tests For Invoice Objects Status Transitions
        $testedTransitions = array(
            "Inv: Draft   "     => array(Status::DRAFT,       Status::DRAFT,         false),
            "Inv: Cancel  "     => array(Status::CANCELED,    Status::CANCELED,      false),
            "Inv: Re Draft"     => array(Status::DRAFT,       Status::DRAFT,         false),
            "Inv: Valid   "     => array(Status::PAYMENT_DUE, Status::PAYMENT_DUE,   false),
            "Inv: Done    "     => array(Status::COMPLETE,    Status::COMPLETE,      true),
            "Inv: Partial "     => array(Status::COMPLETE,    Status::PAYMENT_DUE,   false),
            "Inv: Done 2  "     => array(Status::COMPLETE,    Status::COMPLETE,      true),
        );

        foreach ($this->sequencesProvider() as $name => $sequence) {
            foreach ($testedTransitions as $description => $testedTransition) {
                $stepName = sprintf("%s->%s", $name, $description);
                $results[$stepName] = array_merge($sequence, $testedTransition);
            }
        }

        return $results;

    }

    /**
     * Get Invoice Dataset for Testing
     *
     * @param string $status Expected Invoice Status
     * @param bool $withPayment Add Payment Details
     */
    private function getDatasetOverrides(string $status, bool $withPayment = false): array
    {
        //====================================================================//
        // Create Fake Invoice Dataset
        $fakeData = array(
            "state" => $status,
        );

        //====================================================================//
        // Force Items Qty & Prices
        $fakeData = array_replace_recursive($fakeData, array(
            "lines" => array(
                "0" => array(
                    "quantity" => 1,
                    "discount" => 0,
                    "price_unit" => array("ht" => 10, "ttc" => 10, "tax" => 0, "vat" => 0)
                ),
                "1" => array(
                    "quantity" => 1,
                    "discount" => 0,
                    "price_unit" => array("ht" => 10, "ttc" => 10, "tax" => 0, "vat" => 0)
                ),
            )
        ));

        //====================================================================//
        //   Force Payments
        if ($withPayment) {
            $fakeData = array_replace_recursive(
                $fakeData, $this->getFakePayments()
            );
        }

        return $fakeData;
    }

    /**
     * Get Fake Invoice Payments Dataset
     */
    private function getFakePayments(): array
    {
        //====================================================================//
        // Generate Associated fields Collection
        $fieldsIds = TestFields::getAll("Invoice")
            ->filterIdentifiers(array(
                "journal_code@payments",
                //====================================================================//
                // Payment Fields in V12 & V13
                "payment_date@payments",
                "communication@payments",
                //====================================================================//
                // Payment Fields in V14 ++
                "date@payments",
                "ref@payments",
            ))
        ;
        //====================================================================//
        // Generate Dataset
        $fakeData =  Generator::fromCollection($fieldsIds);

        //====================================================================//
        // Force Payments Amounts
        return array_replace_recursive($fakeData, array(
            "payments" => array(
                "0" => array("amount" => 10),
                "1" => array("amount" => 10.1),
            )
        ));
    }
}
