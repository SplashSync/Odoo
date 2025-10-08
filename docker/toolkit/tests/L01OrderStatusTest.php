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
use Splash\Core\Client\Splash;
use Splash\Core\Dictionary\Objects\Order\Status;
use Splash\Core\Helpers\ObjectsHelper;
use Splash\Validator\Phpunit\TestContext as Context;
use Splash\Validator\Phpunit\Tests\ObjectCrudTest;
use Splash\Validator\Phpunit\TestSequences;
use Splash\Validator\SplashTestCase;
use Splash\Validator\Phpunit\TestObjects;
use Splash\Validator\Phpunit\TestFields;

/**
 * Local Test Suite - Verify Writing of Orders Status
 */
class L01OrderStatusTest extends SplashTestCase
{
    const TYPE = "Order";

    /**
     * @var array
     */
    private static $objectsIds = array();

    /**
     * Create Orders Objects for Testing
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
            ->setDatasetOverrides(array(
                'state' => Status::DRAFT,
            ))
            ->executeWriteTest()
        ;
        //====================================================================//
        // Store Order ID for next Tests
        Assert::assertNotEmpty($objectId = Context::objectId());
        Assert::assertIsString($objectId);
        self::$objectsIds[$sequence] = $objectId;
        //====================================================================//
        // Ensure Minimal Stock
        foreach (Context::dataset()['lines'] ?? array() as $line) {
            $productId = ObjectsHelper::id($line['product_id']);
            Assert::assertNotEmpty($productId);
            Assert::assertNotEmpty(Splash::object("Product")->set($productId, array(
                    "qty_available" => $line['product_uom_qty'] + 10000,
            )));
        }
    }

    /**
     * Test Order Status
     *
     * @dataProvider orderStatusProvider
     *
     * @return void
     * @throws Exception
     */
    public function testStatusChanges(
        string $sequence,
        string $newStatus,
        string $expectedStatus,
        bool $allowFailure = false
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
        // Update Status Directly on Module
        Context::setObjectId(self::$objectsIds[$sequence]);
        Context::setDataset($dataset = array("state" => $newStatus));
        Context::setDatasetOverrides(array());
        Splash::object(self::TYPE)->lock();
        $objectId = Splash::object(self::TYPE)
            ->set(self::$objectsIds[$sequence], $dataset)
        ;
        //====================================================================//
        // Update May Fail
        if (empty($objectId)) {
            $this->assertNotEmpty($allowFailure);

            return;
        }
        $this->assertNotEmpty($objectId);
        $this->assertEquals(self::$objectsIds[$sequence], $objectId);
        //====================================================================//
        // Load Object
        $object = Splash::object(self::TYPE)->get($objectId, $this->getReadFieldsList());
        $this->assertNotEmpty($object);
        //====================================================================//
        //   Check Status
        $this->assertEquals($expectedStatus, $object['state']);
        //====================================================================//
        //   Check Name
        $this->assertNotEmpty($object["name"]);
        $this->assertNotEquals("New", $object["name"]);
        //====================================================================//
        //   Check Lines
        foreach ($object["lines"] ?? array() as $line) {
            //====================================================================//
            // Check Ordered Qty
            $this->assertNotEmpty($line["product_uom_qty"], "Ordered Qty is Empty");
            //====================================================================//
            // Check Product Type
            $this->assertNotEmpty($line["detailed_type"], "Product Type is Empty");
            if ($line["detailed_type"] != "consu") {
                continue;
            }
            //====================================================================//
            // Check Reserved Qty
            if (Status::isValidated($expectedStatus)) {
                    $this->assertNotEmpty($line["qty_reserved"], "Reserved Qty is Empty");
                    $this->assertEquals(
                        $line["product_uom_qty"],
                        $line["qty_reserved"],
                        "Ordered & Reserved Qty are different"
                    );
            }
            //====================================================================//
            // Check Delivered Qty
            if (Status::isDelivered($expectedStatus)) {
                $this->assertNotEmpty($line["qty_delivered"], "Delivered Qty is Empty");
                $this->assertEquals(
                    $line["product_uom_qty"],
                    $line["qty_delivered"],
                    "Ordered & Delivered Qty are different"
                );
            }
        }
    }

    /**
     * @return array
     */
    public static function orderStatusProvider(): array
    {
        $result = array();
        $states = array(
            //====================================================================//
            //   Tests For Order Objects
            "Order: Draft "     => array(Status::DRAFT,       Status::DRAFT),
            "Order: Cancel"     => array(Status::CANCELED,    Status::CANCELED),
            "Order: Not Valid"  => array(Status::PROCESSING,  Status::CANCELED, true),
            "Order: Re Draft "  => array(Status::DRAFT,       Status::DRAFT),
            "Order: Valid "     => array(Status::PROCESSING,    Status::PROCESSING),
            "Order: Done  "     => array(Status::DELIVERED,    Status::DELIVERED),
        );
        //====================================================================//
        // Walk on Test Sequences
        foreach (TestSequences::getAll() as $sequence) {
            //====================================================================//
            // Configure Env. for Test Sequence
            TestSequences::configure($sequence);
            //====================================================================//
            // For Each Update Test
            foreach ($states as $name => $state) {
                //====================================================================//
                // Add Test to List
                $dataSetName = '['.$sequence."] ".$name;
                $result[$dataSetName] = array_merge(
                    array('sequence' => $sequence),
                    $state,
                );
            }
        }

        return $result;
    }

    /**
     * Get List of Fields to Read
     *
     * @return string[]
     */
    private function getReadFieldsList(): array
    {
        return TestFields::getAllowed(self::TYPE)->filterRead()->reduce();
    }
}
