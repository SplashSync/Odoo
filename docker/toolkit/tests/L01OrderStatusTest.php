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

namespace Splash\Local\Tests;

use Exception;
use Splash\Client\Splash;
use Splash\Tests\Tools\ObjectsCase;
use Splash\Models\Objects\Order\Status;

/**
 * Local Test Suite - Verify Writing of Orders Status
 */
class L01OrderStatusTest extends ObjectsCase
{
    /**
     * @var array
     */
    private static $objectsIds = array();

    /**
     * @throws Exception
     *
     * @return void
     */
    public function testCreateObjects(): void
    {
        $order = $this->createObject("Order", Status::DRAFT);
    }

    /**
     * Test Order Status
     *
     * @dataProvider statusProvider
     *
     * @param string      $objectType
     * @param string      $newStatus
     * @param string      $expectedStatus
     *
     * @return void
     * @throws Exception
     */
    public function testStatusChanges(
        string $objectType,
        string $newStatus,
        string $expectedStatus
    ): void {
        //====================================================================//
        //   Update Status Directly on Module
        Splash::object($objectType)->lock();
        $objectId = Splash::object($objectType)
            ->set(self::$objectsIds[$objectType], array("state" => $newStatus))
        ;
        $this->assertNotEmpty($objectId);
        $this->assertEquals(self::$objectsIds[$objectType], $objectId);
        //====================================================================//
        //   Load Object
        $object = Splash::object($objectType)->get($objectId, $this->getReadFieldsList($objectType));
        $this->assertNotEmpty($object);
        $this->assertEquals($expectedStatus, $object['state']);
        //====================================================================//
        //   Check Status
        $this->assertNotEmpty($object["name"]);
        $this->assertNotEquals("New", $object["name"]);
        //====================================================================//
        //   Check Lines
        foreach ($object["lines"] ?? array() as $line) {
            //====================================================================//
            //   Check Ordered Qty
            $this->assertNotEmpty($line["product_uom_qty"], "Ordered Qty is Empty");
            //====================================================================//
            //   Check Product Type
            $this->assertNotEmpty($line["detailed_type"], "Product Type is Empty");
            if ($line["detailed_type"] != "consu") {
                continue;
            }
            //====================================================================//
            //   Check Reserved Qty
            if (Status::isValidated($expectedStatus)) {
                    $this->assertNotEmpty($line["qty_reserved"], "Reserved Qty is Empty");
                    $this->assertEquals(
                        $line["product_uom_qty"],
                        $line["qty_reserved"],
                        "Ordered & Reserved Qty are different"
                    );
            }
            //====================================================================//
            //   Check Delivered Qty
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
    public function statusProvider(): array
    {
        return array(
            //====================================================================//
            //   Tests For Order Objects
            "Order: Draft "     => array("Order",      Status::DRAFT,       Status::DRAFT),
            "Order: Cancel"     => array("Order",      Status::CANCELED,    Status::CANCELED),
            "Order: Not Valid"  => array("Order",      Status::PROCESSING,  Status::CANCELED),
            "Order: Re Draft "  => array("Order",      Status::DRAFT,       Status::DRAFT),
            "Order: Valid "     => array("Order",      Status::PROCESSING,    Status::PROCESSING),
            "Order: Done  "     => array("Order",      Status::DELIVERED,    Status::DELIVERED),
        );
    }

    /**
     * @param string $objectType
     * @param string $status
     *
     * @return array
     * @throws Exception
     */
    private function createObject(string $objectType, string $status): array
    {
        //====================================================================//
        //   Create Fake Order Data
        $fields = $this->fakeFieldsList($objectType, array(), true);
        $fakeData = $this->fakeObjectData($fields);
        $fakeData["state"] = $status;
        //====================================================================//
        //   Execute Action Directly on Module
        Splash::object($objectType)->lock();
        $objectId = Splash::object($objectType)->set(null, $fakeData);
        $this->assertNotEmpty($objectId);
        $this->assertIsString($objectId);
        //====================================================================//
        //   Add Object Id to Created List
        $this->addTestedObject($objectType, $objectId);
        self::$objectsIds[$objectType] = $objectId;
        //====================================================================//
        //   Load Object
        $object = Splash::object($objectType)->get($objectId, $this->getReadFieldsList($objectType));
        $this->assertNotEmpty($object);
        $this->assertEquals($status, $object["state"]);

        return $object;
    }

    /**
     * Get List of Fields to read
     *
     * @param string $objectType
     *
     * @return string[]
     *
     * @throws Exception
     */
    private function getReadFieldsList(string $objectType): array
    {
        return array_merge(
            $this->reduceFieldList($this->fakeFieldsList($objectType, array(), true), true),
            array("name", "qty_delivered@lines", "qty_reserved@lines", "detailed_type@lines"),
        );
    }
}
